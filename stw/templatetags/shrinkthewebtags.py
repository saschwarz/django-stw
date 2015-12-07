"""
Django template tags for inserting Shrink The Web images into templates.

There are two templatetags:
 - shrinkthewebimage - the original image insertion templatetag that implements
the STW preview feature. STW requires free accounts to use this tag. PRO accounts
can use this tag to access the preview feature.
 - stwimage - the non-preview templatetag that supports all PRO features.
"""
import urllib
from django.conf import settings
from django import template

class STWConfigError(template.TemplateSyntaxError):
    pass

class FormatSTWFreeImageNode(template.Node):

    def __init__(self, url, **kwargs):
        params = {}
        # load defaults if any
        params.update(settings.SHRINK_THE_WEB)
        # overwrite defaults for this tag instance
        params.update(kwargs)
        self.kwargs = params
        self.url = url
        self._validate()

    def _validate(self):
        if 'stwaccesskeyid' not in self.kwargs:
            raise STWConfigError("'stwaccesskeyid' must be defined in settings.SHRINK_THE_WEB")
        if 'stwsize' not in self.kwargs:
            raise template.TemplateSyntaxError("'shrinkthewebimage' tag requires 'stwsize' keyword")

    @classmethod
    def _resolve(cls, var, context):
        """if var is a string then return it otherwise use it to lookup a value in the current context"""
        if var[0] == var[-1] and var[0] in ('"', "'"):
            var = var[1:-1] # a string
        else:
            var = template.Variable(var).resolve(context)
        return var

    def _create_urlencoded_options(self, options):
        """Create JSON dictionary of option excluding 'stwaccesskeyid', 'stwlang' and 'stwsize'"""
        ret = {}
        for k,v in options.items():
            if k not in ('stwaccesskeyid', 'stwsize', 'lang'):
                ret[k] = v
        return ret and urllib.urlencode(ret) or None

    def render(self, context):
        args = [self._resolve(self.url, context),
                self.kwargs['stwaccesskeyid'],
                self.kwargs['stwsize'],
                self.kwargs.get('lang', 'en')]
        options = self._create_urlencoded_options(self.kwargs)
        if options:
            args.append(options)
        return """<script type="text/javascript">stw_pagepix({0!s});</script>""".format(",".join(["\'{0!s}\'".format(arg) for arg in args]))


class FormatSTWImageNode(FormatSTWFreeImageNode):

    def __init__(self, url, alt, **kwargs):
        if 'stwembed' not in kwargs:
            kwargs['stwembed'] = 1 # default to image
        self.alt = alt
        super(FormatSTWImageNode, self).__init__(url, **kwargs)

    def _validate(self):
        if 'stwaccesskeyid' not in self.kwargs:
            raise STWConfigError("'stwaccesskeyid' must be defined in settings.SHRINK_THE_WEB")
        # validate conflicting options
        if 'stwsize' in self.kwargs:
            if 'stwxmax' in self.kwargs or 'stwymax' in self.kwargs or 'stwfull' in self.kwargs:
                raise template.TemplateSyntaxError("'stwimage' tag does not allow 'stwsize' and ('stwfull' or ('stwxmax' and/or 'stwymax')) keyword(s)")
        elif 'stwxmax' not in self.kwargs and 'stwymax' not in self.kwargs and 'stwfull' not in self.kwargs:
            raise template.TemplateSyntaxError("'stwimage' tag requires 'stwsize' or ('stwfull' or ('stwxmax' and/or 'stwymax')) keyword(s)")

    def render(self, context):
        url = self._resolve(self.url, context)
        alt = self._resolve(self.alt, context)
        encoded = urllib.urlencode(self.kwargs)
        if encoded:
            encoded += '&'
        result =  '''<img src="http://images.shrinktheweb.com/xino.php?{0!s}stwurl={1!s}" alt="{2!s}"/>'''.format(encoded, url, alt)
        return result


def do_shrinkthewebimage(parser, token):
    """
    Original templatetag designed for use by free accounts and using STW's
    verification JavaScript API. PRO account key-value options are also
    supported

    Usage::

        {% load shrinkthewebtags %}
        {% stwjavascript %}

        {% shrinkthewebimage url size key-value-pairs %}

    Where:

        ``url``
          is expected to be a variable instantiated from the context
          or a quoted string to be used explicitly.

        ``size``
          is expected to a valid size string accepted by shrinktheweb.com
          which currently accepts one of: "mcr", "tny", "vsm", "sm", "lg"
          or "xlg". A context variable can also be used.

        ``key-value-pairs``
          matching STW API values i.e. stwembed=0 stwinside=1
          minimal validation of key value pairs is performed.
          Only STW PRO accounts can supply these options.

    Examples::

        Given a template context variable "author" with attributes "url" and
        "description" the following are valid entries in a template file:

        {% shrinkthewebimage author.url "xlg"%}

        {% shrinkthewebimage author.url "xlg" stwinside=1 %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError("'{0!s}' tag takes 3 or more arguments".format(bits[0]))
    size = bits[2]
    if size[0] == size[-1] and size[0] in ('"', "'"):
        size = size[1:-1] # a string

    kwargs = {'stwsize' : size,
              }
    for key_equal_value in bits[3:]:
        key, value = key_equal_value.split("=")
        kwargs[str(key.strip())] = value.strip()

    return FormatSTWFreeImageNode(url=bits[1], **kwargs)


def do_stwimage(parser, token):
    """
    Key value based templatetag supporting all STW features for PRO and Plus users.

    Usage::

        {% load shrinkthewebtags %}
        {% stwimage url alt key-value-pairs %}

    Where:

        ``url``
          is expected to be a variable instantiated from the context
          or a quoted string to be used explicitly.

        ``key-value-pairs``
          matching STW API values i.e. stwembed=0 stwinside=1
          minimal validation of key value pairs is performed

    Examples::

        Given a template context variable "author" with attributes "url" and
        "description" the following are valid entries in a template file:

        {% load shrinkthewebtags %}

        get image of the follow the full url (not just the top level page), wait
        5 seconds, and return image in large size (this requires license with PRO
        features:

        {% stwimage author.url author.description stwinside=1 stwdelay=5 stwsize=lrg %}
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError("'{0!s}' tag takes at least 2 arguments".format(bits[0]))

    # process keyword args
    kwargs = {}
    for bit in bits[3:]:
        key, value = bit.split("=")
        if value is '':
            raise template.TemplateSyntaxError("'{0!s}' tag keyword: {1!s} has no argument".format(bits[0], key))

        if key.startswith('stw'):
            kwargs[str(key)] = value
        else:
            raise template.TemplateSyntaxError("'{0!s}' tag keyword: {1!s} is not a valid STW keyword".format(bits[0], key))
    return FormatSTWImageNode(url=bits[1], alt=bits[2] , **kwargs)


def stwjavascript():
    """Insert script tag to load the javascript required by Shrink The Web's API"""
    return """<script type="text/javascript" src="http://www.shrinktheweb.com/scripts/pagepix.js"></script>"""


register = template.Library()
register.tag('shrinkthewebimage', do_shrinkthewebimage)
register.tag('stwimage', do_stwimage)
register.simple_tag(stwjavascript)
