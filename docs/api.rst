Developer Interface
===================

Session
-------

.. automodule:: pysjtu.session
    :members:

Client
------

.. automodule:: pysjtu.client
    :members:

.. note::
    Anything that has request-compatible `get`, `post` methods and a `_cache_store` dict can be accepted as a `Session`.

Models
------

**Base class for a single result object (a single course, exam, etc.)**

.. autoclass:: pysjtu.model.base.Result
    :members:

**Base class for API return value**

.. autoclass:: pysjtu.model.base.Results
    :members:

**Base class for paged API return value**

.. autoclass:: pysjtu.model.base.QueryResult
    :members:

Recognizers
-----------

.. automodule:: pysjtu.ocr
    :members:
