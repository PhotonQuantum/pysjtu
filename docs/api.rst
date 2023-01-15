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

Recognizers
-----------

.. automodule:: pysjtu.ocr
    :members:

Schema
------

Utilities helpful for creating the model for a new API. If you want to contribute to this project, you may want to read this.

This package uses `marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_
and `marshmallow_dataclass <https://lovasoa.github.io/marshmallow_dataclass>`_ to define the schema of the data.

**Example**

.. sourcecode:: python

    from marshmallow_dataclass import dataclass
    from marshmallow import EXCLUDE
    from pysjtu.fields import SplitField

    @dataclass(base_schema=FinalizeHook(LoadDumpSchema))    # to support separate alias for load and dump
    class Foo(Result):
        bar: str
        baz: int = mfield(required=True, load_key="baz_id")
        names: WithField(List[str], field=SplitField, sep=",") = mfield(required=True)

For more complex use cases, you can read the schema of `GPAQueryParams <https://github.com/PhotonQuantum/pysjtu/blob/master/pysjtu/models/gpa.py>`_ for reference.

.. automodule:: pysjtu.schema
    :members:

Exceptions
----------

.. automodule:: pysjtu.exceptions
    :members:
