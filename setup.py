"""Managing DMARC aggregate and feedback reports
"""
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-dmarc',
    version='0.5.1',
    packages=['dmarc'],
    include_package_data=True,
    license='BSD',
    description='Managing DMARC aggregate and feedback reports',
    long_description=long_description,
    url='http://p-o.co.uk/tech-articles/django-dmarc/',
    download_url='https://pypi.python.org/pypi/django-dmarc',
    author='Alan Hicks',
    author_email='ahicks@p-o.co.uk',
    requires=['django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='dmarc email spf dkim',
)
