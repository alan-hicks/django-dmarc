import os
from setuptools import setup

README=open(os.path.join(os.path.dirname(__file__), 'docs/README.rst')).read()

DESCRIPTION="""
Making it easier to manage DMARC reports
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dmarc',
    version='0.4.1',
    packages=['dmarc'],
    include_package_data=True,
    license='BSD License',
    description=DESCRIPTION,
    long_description=README,
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
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
