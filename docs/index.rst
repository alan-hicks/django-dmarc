.. Django DMARC documentation master file, created by
   sphinx-quickstart on Mon May 12 11:13:16 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
Django DMARC
============

**Managing DMARC aggregate and feedback reports**

Designed to quickly and easily manage DMARC aggregate and feedback reports.

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

5. Import an aggregate report with::

    python manage.py importdmarcreport --email

6. See your aggregated feedback reports from the Admin page at admin/dmarc

7. Import a feedback report with::

    python manage.py importfeedbackreport --email

Copyright
=========

Django DMARC and this documentation is
Copyright (c) 2015-2017, Persistent Objects Ltd.
All rights reserved.

Contributors
============

This list is not complete and not in any useful order, but I would
like to thank everybody who contributed in any way, with code, hints,
bug reports, ideas, moral support, endorsement, or even complaints...
You have made django-dmarc what it is today.

| Thank you,
| Alan Hicks

.. include:: ../AUTHORS

License
=======

This documentation is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/.

The software is licensed under the BSD two clause license.

.. include:: ../LICENSE
