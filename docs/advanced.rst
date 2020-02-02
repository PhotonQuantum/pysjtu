Advanced Usage
==============

Session Object
--------------

The :class:`Session` object contains iSJTU session state, handles login operation, and persists certain parameters and
some inner states across requests. And it has several HTTP request interfaces to help you send requests as a logged user.

Login
+++++

There's several ways to acquire a login session.

First, let's login with username and password:

.. sourcecode:: python

    sess = pysjtu.Session(username="...", password="...")

A `login()` method is provided, in case you want to provide username and password later:

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

Be aware that a session validation will be performed when setting cookies.
If your cookie doesn't contain valid user information, a :class:`SessionException` will be raised.
To skip this validation, set `_cookies`.

.. sourcecode:: python

    sess = pysjtu.Session()
    sess.cookies = some_invalid_cookies  # This will fail.
    sess._cookies = some_invalid_cookies  # This won't.

Session Persistence
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

    sess = pysjtu.Session(session_file="session.file")

Sessions can also be used as context managers. This will make sure the session file is updated when exiting the `with` block,
even if unhandled exceptions occurred.

.. sourcecode:: python

    with pysjtu.Session(session_file="session.file") as sess:
        sess.get(...)

The passed file must exist, or a :class:`FileNotFound` exception will be raised. But passing in an empty file is allowed, emptying username, password and cookies.

Configuration
+++++++++++++

Sessions can be used to provide configs to requests. Just like Sessions in `requests` and Clients in `HTTPX`, this is
done by setting the properties.

.. sourcecode:: python

    s = pysjtu.Session()
    s.proxies = {"http": "http://127.0.0.1:8888", "https": "http://127.0.0.1:8888"}
    s.timeout = 1.0

HTTP Requests
+++++++++++++

You can use a :class:`Session` to send HTTP requests as a logged user:

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

HTTP Proxying
-------------

PySJTU supports HTTP proxies.

To forward all traffic to `http://127.0.0.1:8888`, you may set the proxy information at :class:`Session` initialization,
or set the `proxies` property.

.. sourcecode:: python

    s = pysjtu.Session(proxies="http://127.0.0.1:8888")
    # or
    s.proxies = "http://127.0.0.1:8888"

For detailed usage, refer to `HTTPX: HTTP Proxying <https://www.python-httpx.org/advanced/#http-proxying>`_.

Timeout Configuration
---------------------

Like HTTPX, PySJTU has strict timeouts.

Timeouts can be enforced request-wise and session-wise.

.. sourcecode:: python

    s = pysjtu.Session(timeout=10)
    s.get("https://i.sjtu.edu.cn", timeout=10)

For detailed usage, refer to `HTTPX: Fine tunning the configuration <https://www.python-httpx.org/advanced/#fine-tuning-the-configuration>`_.
