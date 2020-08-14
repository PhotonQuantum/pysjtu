Advanced Usage
==============

AsyncSession Object
--------------

The :class:`AsyncSession` object contains iSJTU session state, handles login operation, and persists certain parameters and
some inner states across requests. And it has an HTTP request interface to help you send requests as a logged user.

In the :ref:`QuickStart`, we use `create_client` function to acquire a :class:`Client`. Under the hood, `create_client`
creates a :class:`AsyncSession` for you. But if you need features like session persistence, proxies and tuned timeout, you
need to create the session manually.

Login
+++++

There's several ways to acquire a login session.

First, let's login with username and password:

.. sourcecode:: python

    sess = pysjtu.AsyncSession(username="...", password="...")

A `login()` method is provided, in case you want to provide username and password later:

.. sourcecode:: python

    sess = pysjtu.AsyncSession()
    sess.login("username", "password")

And, if you have cookie contains session info, you may login with this cookie:

.. sourcecode:: python

    sess = pysjtu.AsyncSession(cookies=...)

The `cookies` parameter accepts any cookie type that HTTPX accepts (currently `HTTPX.Cookies`, `CookieJar`, and `dict`).
Also, cookies can be set later:

.. sourcecode:: python

    sess = pysjtu.AsyncSession()
    sess.cookies = ...

Be aware that a session validation will be performed when setting cookies.
If your cookie doesn't contain valid user information, a :class:`SessionException` will be raised.
To skip this validation, set `_cookies`.

.. sourcecode:: python

    sess = pysjtu.AsyncSession()
    sess.cookies = some_invalid_cookies  # This will fail.
    sess._cookies = some_invalid_cookies  # This won't.

AsyncSession Persistence
+++++++++++++++++++

You may want to dump your login session to use it later.

To persist your session, you simply call the `dump(s)` function. The `dump()` function will return a dict containing session info.
And the `dumps(...)` function will save session info to your specified file.

.. sourcecode:: python

    logged_sess.dump()
    # {'username': '...', 'password': '...', 'cookies': {...}}
    logged_sess.dumps("session.file")  # session saved to ./session.file
    logged_sess.dumps(f)  # session saved to 'f' file-like object

Similarly, to load your saved session, you call the `load(s)` function.

.. sourcecode:: python

    sess.load({...})
    sess.loads("session.file")
    sess.loads(f)

Besides, saved session files can be loaded when initializing the object:

.. sourcecode:: python

    sess = pysjtu.AsyncSession(session_file="session.file")

Sessions can also be used as context managers. This will make sure the session file is updated when exiting the `with` block,
even if unhandled exceptions occurred.

.. sourcecode:: python

    with pysjtu.AsyncSession(session_file="session.file") as sess:
        sess.get(...)

The passed file must exist, or a :class:`FileNotFound` exception will be raised. But passing in an empty file is allowed, emptying username, password and cookies.

Configuration
+++++++++++++

Sessions can be used to provide configs to requests. Just like Sessions in `requests` and Clients in `HTTPX`, this is
done by passing parameters to the :class:`Client` constructor.

.. sourcecode:: python

    s = pysjtu.AsyncSession(cookies=..., proxies="http://127.0.0.1:8888", timeout=1.0)

HTTP Requests
+++++++++++++

You can use a :class:`AsyncSession` to send HTTP requests as a logged user:

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

If the session is expired, and username and password hasn't been provided (you login by providing cookies only),
a :class:`SessionException` will be raised. If the provided username and password is invalid, a :class:`LoginException` will be raised.

To skip this validation, set `validate_session` to False. To disable session renewal, set `auto_renew` to False.

Beware that if `validate_session` is True, `auto_renew` is False, and your session is expired, a :class:`SessionException`
will be raised.

.. sourcecode:: python

    s.get("https://i.sjtu.edu.cn/...", validate_session=False)
    s.get("https://i.sjtu.edu.cn/...", auto_renew=False)

Client Object
-------------

The :class:`Client` object provides a developer-friendly interface to iSJTU APIs. It depends on an authenticated
:class:`AsyncSession` object to send HTTP requests.

Initialization
++++++++++++++

To initialize a :class:`Client` object, you pass in a :class:`AsyncSession` object described in the previous section.

.. sourcecode:: python

    client = pysjtu.Client(session=sess)

Be aware that the new `client` object is bounded with the `session` passed in, which means API calls may alter the `session`'s
internal states (cookies, etc). You may change `session`'s settings at any time, and these changes will reflect on `client`
behaviours immediately.

If you haven't initialized any :class:`AsyncSession` yet and you want to login with a pair of username & password, the
`create_client` function will help you get one and initialize a :class:`Client`.

.. sourcecode:: python

    client = pysjtu.create_client("username", "password")

Usages
++++++

There are two types of API: properties and methods. For detailed usage, see :ref:`iSJTU Interface`.

HTTP Proxying
-------------

PySJTU supports HTTP proxies.

To forward all traffic to `http://127.0.0.1:8888`, you may set the proxy information at :class:`AsyncSession` initialization.

.. sourcecode:: python

    s = pysjtu.AsyncSession(proxies="http://127.0.0.1:8888")

For detailed usage, refer to `HTTPX: HTTP Proxying <https://www.python-httpx.org/advanced/#http-proxying>`_.

Timeout Configuration
---------------------

Like HTTPX, PySJTU has strict timeouts.

Timeouts can be enforced request-wise and session-wise.

.. sourcecode:: python

    s = pysjtu.AsyncSession(timeout=10)
    s.get("https://i.sjtu.edu.cn", timeout=10)

For detailed usage, refer to `HTTPX: Fine tunning the configuration <https://www.python-httpx.org/advanced/#fine-tuning-the-configuration>`_.

OCR
---

During login, captcha is solved automatically using built-in OCR engines. There are two OCR engines you may choose from:
SVMRecognizer and NNRecognizer. For detailed comparison, see :ref:`Developer Interface`.

You may pick a specific engine by passing it to the :class:`AsyncSession` constructor.

.. sourcecode:: python

    s = pysjtu.AsyncSession(ocr=pysjtu.LegacyRecognizer())
