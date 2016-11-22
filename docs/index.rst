.. Django DMARC documentation master file, created by
   sphinx-quickstart on Mon May 12 11:13:16 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
Django DMARC
============

**Making it easier to manage DMARC reports**

Designed to quickly and easily import DMARC reports.

Contents
========

.. toctree::
   :maxdepth: 1

   README
   changelog

Quick start
-----------

1. Install the app

2. Add "dmarc" to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'dmarc',
    )

3. Add dmarc.urls to your urls::

    from dmarc import urls as dmarc_urls

    urlpatterns = [
        ...
        url(r"^dmarc/", include(dmarc_urls)),
    ]

4. Run 'python manage.py migrate' to create the database models.

5. Import a report with::

    python manage.py importdmarcreport --email

6. See your aggregated feedback reports from the Admin page at admin/dmarc

Copyright
=========

Django DMARC and this documentation is
Copyright (c) 2015-2016, Persistent Objects Ltd.
All rights reserved.

License
=======

This documentation is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/.

The software is licensed under the BSD two clause license.

.. include:: ../LICENSE
