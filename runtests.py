#!/usr/bin/env python

from os.path import dirname, abspath
import sys
import django

from django.conf import settings as django_settings

if not django_settings.configured:
    django_settings.configure(
        DATABASE_ENGINE='sqlite3',
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        },
        INSTALLED_APPS=(
            'stw',
        ),
        SHRINK_THE_WEB='',
        ROOT_URLCONF='django-stw.tests.test_urls',
    )

from django.test.utils import get_runner

def runtests(*test_args):
    if not test_args:
        test_args = ['stw']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    try:
        django.setup()
    except AttributeError:
        pass  # old versions of Django don't have this
    TestRunner = get_runner(django_settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(bool(failures))

    # from django.test.simple import run_tests
    # failures = run_tests(test_args, verbosity=1, interactive=True)
    # sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
