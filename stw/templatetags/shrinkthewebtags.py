"""
Django template tags for inserting Shrink The Web images into templates.

There is one templatetag:
 - stwimage - supports all free and PRO features.

 - shrinkthewebimage - the original image insertion templatetag that implements
the STW preview feature. This is DEPRECATED.
"""
from collections import OrderedDict
from six.moves.urllib import parse
from django.conf import settings
from django import template


class STWConfigError(template.TemplateSyntaxError):
    pass

class FormatSTWImageNode(template.Node):

    def __init__(self, url, alt, **kwargs):
        self.url = url
        self.alt = alt
        params = OrderedDict()
        # load defaults if any
        params.update(settings.SHRINK_THE_WEB)
        if 'stwembed' not in kwargs:
            params['stwembed'] = 1 # default to image
        # overwrite defaults for this tag instance
        params.update(kwargs)
        self.kwargs = params
        self._validate()

    @classmethod
    def _resolve(cls, var, context):
        """if var is a string then return it otherwise use it to lookup a value in the current context"""
        if var[0] == var[-1] and var[0] in ('"', "'"):
            var = var[1:-1] # a string
        else:
            var = template.Variable(var).resolve(context)
        return var

    def _validate(self):
        if 'stwaccesskeyid' not in self.kwargs:
            raise STWConfigError("'stwaccesskeyid' must be defined in settings.SHRINK_THE_WEB")

    def render(self, context):
        url = self._resolve(self.url, context)
        alt = self._resolve(self.alt, context)
        encoded = parse.urlencode(self.kwargs)
        if encoded:
            encoded += '&'
        result =  '''<img src="http://images.shrinktheweb.com/xino.php?{0}stwurl={1}" alt="{2}"/>'''.format(encoded, url, alt)
        return result


def do_stwimage(parser, token):
    """
    Key value based templatetag supporting all STW features for Free and PRO accounts.

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
        raise template.TemplateSyntaxError("'{}' tag takes at least 2 arguments".format(bits[0]))

    # process keyword args
    kwargs = {}
    for bit in bits[3:]:
        key, value = bit.split("=")
        if value is '':
            raise template.TemplateSyntaxError("'{0}' tag keyword: {1} has no argument".format(bits[0], key))

        if key.startswith('stw'):
            kwargs[str(key)] = value
        else:
            raise template.TemplateSyntaxError("'{0}' tag keyword: {1} is not a valid STW keyword".format(bits[0], key))
    return FormatSTWImageNode(url=bits[1], alt=bits[2] , **kwargs)


register = template.Library()
register.tag('stwimage', do_stwimage)
