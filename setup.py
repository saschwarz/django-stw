from setuptools import setup, find_packages

setup(
    name='django-stw',
    version='1.0.1',
    description='This application provides templatetags for simplying using Shrink The Web PagePix',
    author='Steve Schwarz',
    author_email='steve@agilitynerd.com',
    url='https://github.com/saschwarz/django-stw',
    download_url='https://github.com/saschwarz/django-stw/tarball/1.0.1',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords=['Django', 'images', 'templatetag'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools', 'six'],
    test_suite="runtests.runtests",
    tests_require=['mock']
)
