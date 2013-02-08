from setuptools import setup, find_packages

setup(
    name='django-stw',
    version='0.3.0',
    description='This application provides templatetags for simplying using Shrink The Web PagePix',
    author='Steve Schwarz',
    author_email='steve@agilitynerd.com',
    url='http://github.com/saschwarz/django-stw',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools',],
)
