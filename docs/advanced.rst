Advanced Usage
==============

Session Object
--------------

The :class:`pysjtu.session.Session` object contains iSJTU session state, handles login operation, and persists certain parameters and
some inner states across requests. And it has an HTTP request interface to help you send requests as a logged user.

In :ref:`QuickStart`, we used `create_client` function to acquire a :class:`pysjtu.client.Client`. Under the hood, `create_client`
creates a :class:`pysjtu.session.Session` for you. But if you need features like session persistence, proxies and tuned timeout, you
need to create the session manually.

Login
+++++

There's several ways to acquire a login session.

First, let's login with username and password:

.. sourcecode:: python

    sess = pysjtu.Session(username="...", password="...")

A :meth:`pysjtu.session.Session.login` method is provided, in case you want to provide username and password later:

.. sourcecode:: python

    sess = pysjtu.Session()
    sess.login("username", "password")

And, if you have cookie contains session info, you may login with this cookie:

.. sourcecode:: python

    sess = pysjtu.Session(cookies=...)

The `cookies` parameter accepts any cookie type that HTTPX accepts (currently `HTTPX.Cookies`, `CookieJar`, and `dict`).
Also, cookies can be set later:

.. sourcecode:: python

    sess = pysjtu.Session()
    sess.cookies = ...

.. warning::

    A session validation is performed when setting cookies.
    If your cookie doesn't contain valid user information, a :class:`pysjtu.exceptions.SessionException` will be raised.
    To skip this validation, set `_cookies`.

    .. sourcecode:: python

        sess = pysjtu.Session()
        sess.cookies = some_invalid_cookies  # This will fail.
        sess._cookies = some_invalid_cookies  # This won't.

Session Persistence
+++++++++++++++++++

You may want to dump your login session to use it later.

To persist your session, you simply call the :meth:`pysjtu.session.Session.dump` function, which returns a dict containing session info.
And the :meth:`pysjtu.session.Session.dumps` function will save session info to your specified file.

.. sourcecode:: python

    logged_sess.dump()
    # {'username': '...', 'password': '...', 'cookies': {...}}
    logged_sess.dumps("session.file")  # session saved to ./session.file
    logged_sess.dumps(f)  # session saved to 'f' file-like object

Similarly, to load your saved session, you call the :meth:`pysjtu.session.Session.load` and :meth:`pysjtu.session.Session.loads` function.

.. sourcecode:: python

    sess.load({...})
    sess.loads("session.file")
    sess.loads(f)

Besides, saved session files can be loaded when initializing the object:

.. sourcecode:: python

    sess = pysjtu.Session(session_file="session.file")

Sessions can also be used as context managers. This will make sure the session file is updated when exiting the `with` block,
even if unhandled exceptions occurred.

.. sourcecode:: python

    with pysjtu.Session(session_file="session.file") as sess:
        sess.get(...)

.. note::

    The given file must exist, or a :class:`FileNotFound` exception will be raised. But passing in an empty file is allowed, emptying username, password and cookies.

Configuration
+++++++++++++

Sessions can be used to provide configs to requests. Just like Sessions in `requests` and Clients in `HTTPX`, this is
done by passing parameters to the :class:`pysjtu.client.Client` constructor.

.. sourcecode:: python

    s = pysjtu.Session(cookies=..., proxies="http://127.0.0.1:8888", timeout=1.0)

HTTP Requests
+++++++++++++

You can use a :class:`pysjtu.session.Session` to send HTTP requests as a logged user:

.. sourcecode:: python

    s.request("GET", "https://i.sjtu.edu.cn/...")
    s.get("https://i.sjtu.edu.cn/...")
    s.post("https://i.sjtu.edu.cn/...")
    s.put("https://i.sjtu.edu.cn/...")
    s.delete("https://i.sjtu.edu.cn/...")
    s.head("https://i.sjtu.edu.cn/...")
    s.options("https://i.sjtu.edu.cn/...")

They share the same interface with `HTTPX <https://www.python-httpx.org/quickstart/>`_.

By default, a session validation will be performed, and the session will be automatically renewed if it's expired.

.. note::
    Auto session renewal works by automatically login again with the given username and password.

    If the session is expired, and username and password hasn't been provided (you login by providing cookies only),
    :class:`pysjtu.exceptions.SessionException` will be raised. If the provided username and password is invalid,
    :class:`pysjtu.exceptions.LoginException` will be raised.

They can be opt-out by calling request methods with `validate_session`, `auto_renew`, or both set to False.

.. sourcecode:: python

    s.get("https://i.sjtu.edu.cn/...", validate_session=False)
    s.get("https://i.sjtu.edu.cn/...", auto_renew=False)

.. note::

    If `validate_session` is True, `auto_renew` is False, and your session is expired,
    :class:`pysjtu.exceptions.SessionException` will be raised.

Client Object
-------------

The :class:`pysjtu.client.Client` object provides a developer-friendly interface to iSJTU APIs. It uses an authenticated
:class:`pysjtu.session.Session` object to send HTTP requests.

Initialization
++++++++++++++

To initialize a :class:`pysjtu.client.Client` object, you pass in a :class:`pysjtu.session.Session` object described in
the previous section.

.. sourcecode:: python

    client = pysjtu.Client(session=sess)

.. note::
    The new `client` object is bounded with the `session` passed in, which means API calls may alter the `session`'s
    internal states (cookies, etc). You may change `session`'s settings at any time, and these changes will reflect on `client`
    behaviours immediately.

If you haven't initialized any :class:`pysjtu.session.Session` yet and you want to login with a pair of username & password, the
`create_client` function will help you get one and initialize a :class:`pysjtu.client.Client`.

.. sourcecode:: python

    client = pysjtu.create_client("username", "password")

Usages
++++++

There are two types of API: properties and methods. For detailed usage, see :ref:`iSJTU Interface`.

HTTP Proxying
-------------

PySJTU supports HTTP proxies.

To forward all traffic to `http://127.0.0.1:8888`, you may set the proxy information at :class:`pysjtu.session.Session` initialization.

.. sourcecode:: python

    s = pysjtu.Session(proxies="http://127.0.0.1:8888")

For detailed usage, refer to `HTTPX: HTTP Proxying <https://www.python-httpx.org/advanced/#http-proxying>`_.

Timeout Configuration
---------------------

Like HTTPX, PySJTU has strict timeouts.

Timeouts can be enforced request-wise and session-wise.

.. warning::

    A common pitfall is that the default timeout is too short for GPA related requests. To avoid this, you may set the timeout
    separately for these requests.

.. sourcecode:: python

    s = pysjtu.Session(timeout=10)
    s.get("https://i.sjtu.edu.cn", timeout=10)

For detailed usage, refer to `HTTPX: Fine tunning the configuration <https://www.python-httpx.org/advanced/#fine-tuning-the-configuration>`_.

OCR
---

During login, captcha is solved automatically using built-in OCR engines. There are three OCR engines you may choose from:
:class:`pysjtu.ocr.LegacyRecognizer`, :class:`pysjtu.ocr.NNRecognizer` and :class:`pysjtu.ocr.JCSSRecognizer`.

The first two are offline OCR engines, and the last one is an online one.
To use an offline engine, you need to install `PySJTU` with `ocr` extra dependencies.
For detailed comparison, see :ref:`Recognizers`.

The default engine is :class:`pysjtu.ocr.JCSSRecognizer`.
You may pick another one by passing it to the :class:`pysjtu.session.Session` constructor.

.. sourcecode:: python

    s = pysjtu.Session(ocr=pysjtu.NNRecognizer())
    # or to use the client directly,
    c = pysjtu.create_client(ocr=pysjtu.NNRecognizer())
