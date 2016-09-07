=============
Documentation
=============

**Making it easier to manage DMARC reports**

Designed to quickly and easily import DMARC reports.

Quick start
-----------

1. Install the app

2. Add "dmarc" to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'dmarc',
    )

3. Run 'python manage.py migrate' to create the database models.

4. import a report with::

    python manage.py importdmarcreport --email

Usage
=====
python manage.py importdmarcreport

You can choose to import an xml or email file, alternatively with "--email -" you can pipe an email and it will do the right thing.

Description
===========

This Django DMARC project aims to help with implementation of DMARC "Domain-based Message Authentication, Reporting & Conformance" and ongoing monitoring by importing feedback reports about messages that pass and/or fail DMARC evaluation into a more easily digested format.

Perhaps one of the main reasons DMARC is gaining traction amongst organisations of all sizes is a desire to protect their brand and reputation.  By defining and implementing a DMARC policy, an organization can help combat phishing, protect users and their reputation.

Currently at beta stage, importing and data structure are fairly stable, as is reporting.

Choosing Django was an easy choice as it offers an easily built import mechanism and transformation from xml to database through to presentation.

Although it has options for importing either xml or email files, the way it's used here at Persistent Objects is taking the email directly from SMTP and piping it through to the import routine.

We use Exim here and the configuration couldn't be easier

Router::

    dmarcreports:
        driver = accept
        condition = ${if eq{$local_part}{dmarc_report}}
        transport = trans_dmarcreports

Transport::

    trans_dmarcreports:
        driver = pipe
        command = "/usr/local/bin/python2.7 /path/to/manage.py importdmarcreport --email -"
        freeze_exec_fail = true
        return_fail_output = true

DMARC reporting
===============

There is only the one report at dmarc/report/ and requires staff members authorization.

Add the dmarc.urls to your urls::

    from dmarc import urls as dmarc_urls

    urlpatterns = [
        ...
        url(r"^dmarc/", include(dmarc_urls)),
    ]

This is a sample report styled with `Bootstrap`_.

.. image:: images/dmarc-report.png
   :alt: Sample DMARC report

Dependencies
============

* `Django`_ 1.8
* `Bootstrap`_ (optional)

Resources
=========

* `DMARC`_
* `Django`_
* `Google gmail DMARC`_
* `Download from PyPI`_

Support
=======

To report a security issue, please send an email privately to
`ahicks@p-o.co.uk`_. This gives us a chance to fix the issue and
create an official release prior to the issue being made
public.

For general questions or comments, please contact  `ahicks@p-o.co.uk`_.

`Project website`_

Communications are expected to conform to the `Django Code of Conduct`_.

.. GENERAL LINKS

.. _`Django`: http://djangoproject.com/
.. _`Django Code of Conduct`: https://www.djangoproject.com/conduct/
.. _`Python`: http://python.org/
.. _`Persistent Objects Ltd`: http://p-o.co.uk/
.. _`Project website`: http://p-o.co.uk/tech-articles/django-dmarc/
.. _`DMARC`: http://dmarc.org/
.. _`Google gmail DMARC`: https://support.google.com/a/answer/2466580
.. _`Download from PyPI`: https://pypi.python.org/pypi/django-dmarc
.. _`Bootstrap`: http://getbootstrap.com/

.. PEOPLE WITH QUOTES

.. _`Alan Hicks`: https://plus.google.com/103014117568943351106
.. _`ahicks@p-o.co.uk`: mailto:ahicks@p-o.co.uk?subject=django-dmarc+Security+Issue
