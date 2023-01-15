Migration
=========

This page describes how to migrate from an old version of this package to the latest one.

v0.4.x to v0.5.x
----------------

Exception for Invalid Enum Value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Previously, if you tried to send an iSJTU model with an invalid enum value, a **TypeError** would be raised.
Now, an **AttributeError** is raised instead.

GPA Query Parameter Change
~~~~~~~~~~~~~~~~~~~~~~~~~~

`statistics_method` is renamed to `dedup_method` in `GPAQueryParams`, and it's now an enum instead of a string.

v0.3.x to v0.4.x
----------------

Minimum Supported Python Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This version drops support for Python 3.7. Please upgrade to Python 3.8 or later.

Course Selection API Renames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**SelectionClass.drop** is renamed to **SelectionClass.drop**, and **DeregistrationException** is renamed to **DropException**.