"""Tests for custom templatetags"""
import unittest
from mock import Mock, patch
from django.conf import settings
from django import template
from stw.templatetags.shrinkthewebtags import (FormatSTWFreeImageNode,
                                               FormatSTWImageNode,
                                               do_shrinkthewebimage,
                                               do_stwimage,
                                               STWConfigError,
                                               stwjavascript)

class TestFormatSTWFreeImageNode(unittest.TestCase):

    def setUp(self):
        self.settings = settings.SHRINK_THE_WEB
        settings.SHRINK_THE_WEB = {'stwaccesskeyid' : 'key'}

    def tearDown(self):
        settings.SHRINK_THE_WEB = self.settings

    def test_render_strings_url(self):
        # ignore kwarg URL params
        node = FormatSTWFreeImageNode("'url'", **{'stwsize':'sm'})
        def side_effect(*args, **kwargs):
            return 'url'
        node._resolve = Mock(side_effect=side_effect)

        self.assertEqual("""<script type="text/javascript">stw_pagepix('url','key','sm','en');</script>""", node.render(None))

    def test_render_strings_url_lang_default(self):
        settings.SHRINK_THE_WEB = {'stwaccesskeyid': 'key',
                                   'lang': 'fr'}
        node = FormatSTWFreeImageNode("'url'", **{'stwsize':'sm'})
        def side_effect(*args, **kwargs):
            return 'url'
        node._resolve = Mock(side_effect=side_effect)

        self.assertEqual("""<script type="text/javascript">stw_pagepix('url','key','sm','fr');</script>""", node.render(None))


    def test_render_strings_url_lang_local(self):
        settings.SHRINK_THE_WEB = {'stwaccesskeyid': 'key',
                                   'lang': 'fr'}
        node = FormatSTWFreeImageNode("'url'", **{'stwsize':'sm', 'lang':'de'})
        def side_effect(*args, **kwargs):
            return 'url'
        node._resolve = Mock(side_effect=side_effect)

        self.assertEqual("""<script type="text/javascript">stw_pagepix('url','key','sm','de');</script>""", node.render(None))

    def test_render_strings_url_one_option(self):
        node = FormatSTWFreeImageNode("'url'", stwsize='lrg', stwfull=1)
        def side_effect(*args, **kwargs):
            return 'url'
        node._resolve = Mock(side_effect=side_effect)
        self.assertEqual("""<script type="text/javascript">stw_pagepix('url','key','lrg','en','stwfull=1');</script>""", node.render(None))

    def test_render_strings_url_two_options(self):
        node = FormatSTWFreeImageNode("'url'", stwsize='lrg', stwfull=1, stwsomearg='abcde')
        def side_effect(*args, **kwargs):
            return 'url'
        node._resolve = Mock(side_effect=side_effect)
        self.assertEqual("""<script type="text/javascript">stw_pagepix('url','key','lrg','en','stwfull=1&stwsomearg=abcde');</script>""", node.render(None))


class TestSTWImageNode(unittest.TestCase):

    def setUp(self):
        self.settings = settings.SHRINK_THE_WEB
        settings.SHRINK_THE_WEB = {'stwaccesskeyid' : 'key'}

    def tearDown(self):
        settings.SHRINK_THE_WEB = self.settings

    def test_init(self):
        node = FormatSTWImageNode("url", "alt", stwsize='lrg')
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        # get value from settings.SHRINK_THE_WEB
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])

    def test_init_override_key(self):
        node = FormatSTWImageNode("url", "alt", stwaccesskeyid='overridekey', stwsize='lrg')
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        self.assertEqual('overridekey', node.kwargs['stwaccesskeyid'])

    def test_init_add_from_settings_and_override_key(self):
        settings.SHRINK_THE_WEB = {'stwaccesskeyid' : 'key', 'stwanewkey': 'newkey'}
        node = FormatSTWImageNode("url", "alt", stwaccesskeyid='overridekey', stwsize='lrg')
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        self.assertEqual('overridekey', node.kwargs['stwaccesskeyid'])
        self.assertEqual('newkey', node.kwargs['stwanewkey'])


    # valid combinations of size, xmax, ymax
    def test_init_no_stwembed(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwsize':'lrg'})
        self.assertEqual(3, len(node.kwargs.keys()))
        self.assertEqual(1, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual('lrg', node.kwargs['stwsize'])

    def test_init_stwembed(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwembed':0, 'stwsize':'lrg'})
        self.assertEqual(3, len(node.kwargs.keys()))
        self.assertEqual(0, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual('lrg', node.kwargs['stwsize'])

    def test_init_stwembed_stwxmax(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwembed':0, 'stwxmax':100})
        self.assertEqual(3, len(node.kwargs.keys()))
        self.assertEqual(0, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual(100, node.kwargs['stwxmax'])

    def test_init_stwembed_stwymax(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwembed':0, 'stwymax':100})
        self.assertEqual(3, len(node.kwargs.keys()))
        self.assertEqual(0, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual(100, node.kwargs['stwymax'])

    def test_init_stwembed_stwxmax_stwymax(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwembed':0, 'stwymax':200, 'stwxmax':100})
        self.assertEqual(4, len(node.kwargs.keys()))
        self.assertEqual(0, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual(200, node.kwargs['stwymax'])
        self.assertEqual(100, node.kwargs['stwxmax'])

    def test_init_stwembed_stwxfull(self):
        node = FormatSTWImageNode('url', 'alt', **{'stwaccesskeyid':'key', 'stwembed':0, 'stwfull':1})
        self.assertEqual(3, len(node.kwargs.keys()))
        self.assertEqual(0, node.kwargs['stwembed'])
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])
        self.assertEqual(1, node.kwargs['stwfull'])

    # missing required configuration
    def test_init_no_stwaccesskeyid(self):
        settings.SHRINK_THE_WEB = {}
        self.assertRaises(template.TemplateSyntaxError,
                          FormatSTWImageNode,
                          'url', 'alt', stwsize='lrg')

    # invalid combinations of stwsize, stwxmax, stwymax and stwfull
    def test_init_no_stwsize_no_stwxmax_no_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode,
                          'url', 'alt', stwaccesskeyid='key')

    def test_init_stwsize_stwfull(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode,
                          'url', 'alt', **{'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwfull':1})

    def test_init_stwsize_stwxmax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode,
                          'url', 'alt', **{'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwxmax':100})

    def test_init_stwsize_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode,
                          'url', 'alt', **{'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwymax':100})

    def test_init_stwsize_stwxmax_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode,
                          'url', 'alt', **{'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwymax':100, 'stwxmax':100})

    def test_render_context(self):
        node = FormatSTWImageNode("url", "alt", stwsize='lrg')
        results = ["alt", "url"]
        def side_effect(*args, **kwargs):
            return results.pop()
        node._resolve = Mock(side_effect=side_effect)

        context = {'alt': 'contextalt'}
        self.assertEqual('''<img src="http://images.shrinktheweb.com/xino.php?stwaccesskeyid=key&stwsize=lrg&stwembed=1&stwurl=url" alt="alt"/>''', node.render(context))

    @patch('urllib.urlencode')
    def test_render_strings_url_alt_kwargs(self, mockurlencode):
        node = FormatSTWImageNode("'url'", "'alt'", stwsize='lrg')
        results = ["alt", "url"]
        def side_effect(*args, **kwargs):
            return results.pop()
        node._resolve = Mock(side_effect=side_effect)
        mockurlencode.return_value = "kwarg=kwargvalue"
        self.assertEqual('''<img src="http://images.shrinktheweb.com/xino.php?kwarg=kwargvalue&stwurl=url" alt="alt"/>''', node.render(None))


class TestDoShrinkTheWebImage(unittest.TestCase):

    def test_no_args(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=('tagname',))
        self.assertRaises(template.TemplateSyntaxError, do_shrinkthewebimage, parser, token)

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWFreeImageNode')
    def test_correct_args(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("tagname", "url", "lrg"))
        do_shrinkthewebimage(parser, token)
        MockClass.assert_called_with(url="url", stwsize="lrg")

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWFreeImageNode')
    def test_pro_args(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("tagname", "url", "lrg", 'stwinside = 1', 'stwanotherkey = asfd'))
        do_shrinkthewebimage(parser, token)
        MockClass.assert_called_with(url="url", stwsize="lrg", stwinside="1", stwanotherkey='asfd')


class TestDoSTWImage(unittest.TestCase):

    def test_no_args(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=('tagname',))
        self.assertRaises(template.TemplateSyntaxError, do_stwimage, parser, token)

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_no_kwargs(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt")

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_stw_kwarg(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "stwsize=lrg"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt", stwsize="lrg")

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_stw_kwargs(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "stwsize=lrg", "stwembed=1"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt", stwsize="lrg", stwembed='1')

    def test_nonstw_kwarg(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "size=lrg"))
        self.assertRaises(template.TemplateSyntaxError, do_stwimage, parser, token)

class TestSTWJavaScript(unittest.TestCase):

    def test_is_script(self):
        string = stwjavascript()
        self.assertTrue("<script " in string and "</script>" in string)

    def test_correct_url(self):
        string = stwjavascript()
        self.assertTrue("http://www.shrinktheweb.com/scripts/pagepix.js" in string)
