.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Training
========

This module was written to extend the functionality of events to support
trainings and allow you to manage of training actions, training groups,
training hour types, tutors, etc.

Installation
============

To install this module, you need to:

* Install https://github.com/grupoesoc/odoo-grupoesoc-addons.

Configuration
=============

No configuration is needed.

Usage
=====

To use this module, you need to:

* Have *Training / User* or *Training / Manager* permissions.
* Go to the new menu item called *Training*.

There you can find the following:

Hour Types
----------

Hours in each training action are separated by type. Types of hours can be *On
site, Online, Remote* and anything you decide.

Action Types
------------

Depending on the type of hours that a training action is expected to have, the
training action has that action type. For instance:

- A training of type *on-site* may expect only *on-site* hours.
- A training of type *online* may expect only *online* hours.
- A training of type *remote* may expect only *remote* hours.
- A training of type *mixed* may expect *on-site*, *online* and *remote* hours.

Actions
-------

Training actions define the structure of a course.

They have a name, such as *Prevention of occupational hazards, Office
software, Odoo user basic training*, etc.

They also belong to a training type, and depending on it, they define how many
hours of each type are expected to be teached.

Groups
------

A training group is a course that belongs to a training action.

They have all details about it: students, teachers, tutors, start and end
dates, etc.

Technically speaking, groups are just events that are assigned to a training
action. Therefore, you can use also the events view to manage training groups,
but the *Training* menu seems a more consistant place to manage training
groups.

Tutors
------

Tutors are specified for each training group.

A tutor is a special teacher that oversees the whole group. Whenever a student
has a doubt in a non-on-site class, they usually reach a tutor (via email,
phone, etc.) to ask them. Also, tutors may actively review the students'
progress. You can have as many tutors as you want for each training group.

For further information, please visit:

* https://github.com/grupoesoc/odoo-grupoesoc-addons
* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* See `bug tracker`_.

Bug Tracker
===========

In case of trouble, please check there if your issue has already been reported
in the `bug tracker`_. If you spotted it first, help us smashing it by
providing a detailed and welcomed feedback_.

Credits
=======

Contributors
------------

* Jairo Llopis <j.llopis@grupoesoc.es>

Maintainer
----------

This module is maintained by `Grupo ESOC`_.

.. _bug tracker: https://github.com/grupoesoc/odoo-grupoesoc-addons/issues
.. _feedback: https://github.com/grupoesoc/odoo-grupoesoc-addons/issues/new?body=module:%20training%0Aversion:%203.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**
.. _Grupo ESOC: http://grupoesoc.es
