from os import path

from flask import Flask, redirect, session, request

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/website')

app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = b'j(92IdXM+z_3xec]G'

UUID = "ad7283af-2198-476f-95ac-fa9356a0357c"


@app.route("/jaccount/captcha")
def login_captcha():
    return "OK"


@app.route("/jaccount/jalogin")
def login_ja():
    return "OK"


@app.route("/xtgl/login_slogin.html")
def login_isjtu():
    return app.send_static_file("login_slogin.html")


@app.route("/jaccountlogin")
def login():
    return app.send_static_file("jalogin")


@app.route("/login_patch")
def login_patch():
    session["is_login"] = True
    return redirect("/xtgl/index_initMenu.html")


@app.route("/jaccount/ulogin", methods=["post"])
def login_post():
    v = request.args.get("v")
    uuid = request.args.get("uuid")
    username = request.args.get("user")
    password = request.args.get("pass")
    captcha = request.args.get("captcha")
    if uuid == UUID and v == "" and username == "FeiLin" and password == "WHISPERS" and captcha == "ipsum":
        return redirect("https://i.sjtu.edu.cn/login_patch")
    else:
        return redirect("/jaccount/jalogin?err=1")


@app.route("/expire_me")
def session_expire():
    session["is_login"] = False
    return "OK"


@app.route("/is_login")
def is_login():
    return "True" if session.get("is_login", None) else "False"


@app.route("/logout")
def logout():
    session["is_login"] = False
    return redirect("/xtgl/login_slogin.html")


@app.route("/503")
def service_unavailable():
    return "ServiceUnavailable", 503


@app.route("/404")
def not_found():
    return "NotFound", 404


@app.route("/ping", methods=["GET", "HEAD", "PUT", "PATCH", "DELETE"])
def get_and_head():
    return "pong"

@app.route("/ping", methods=["POST"])
def post():
    return request.data


# --------------------------------------
@app.route("/xtgl/index_initMenu.html")
def homepage():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    return app.send_static_file("index_initMenu.html")
