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

Description
===========

This Django DMARC project aims to ease implementating DMARC
"Domain-based Message Authentication, Reporting & Conformance" and
ongoing monitoring by importing aggregate and feedback reports about messages
that pass and/or fail DMARC evaluation into a more easily digested format.

Perhaps one of the main reasons DMARC is gaining traction amongst
organisations of all sizes is a desire to protect their people, brand and
reputation.
By defining and implementing a DMARC policy, an organization can help combat
phishing, protect users and their reputation.

At beta stage, the application is stable, with most efforts on improving
usability and documentation.

Choosing Django was an easy choice as it offers an easily built import
mechanism and transformation from xml to database through to presentation.

Although it has options for importing either xml or email files, zero
maintenance is achieved by fully automating import of feedback and reports.

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
