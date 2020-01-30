from os import path

from flask import Flask, redirect, session, request

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/website')

app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = b'j(92IdXM+z_3xec]G'

UUID = "ad7283af-2198-476f-95ac-fa9356a0357c"
SU = "519027910001"


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


@app.route("/xtgl/index_cxshjdAreaFive.html")
def calendar():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    return app.send_static_file("index_cxshjdAreaFive.html")


@app.route("/cjgl/common_cxGnzdxxList.html")
def gpa_query_params():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.args.get("su", None) != SU:
        return ""
    return app.send_static_file("common_cxGnzdxxList.html")


@app.route("/kbcx/xskbcx_cxXsKb.html", methods=["post"])
def schedule():
    _args = ["xqm", "xnm"]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    return app.send_static_file("xskbcx_cxXsKb.html")


@app.route("/cjcx/cjcx_cxXsXmcjList.html", methods=["post"])
def score_detail():
    _args = ["xnm", "xqm", "jxb_id", "_search", "nd", "queryModel.showCount", "queryModel.currentPage",
             "queryModel.sortName", "queryModel.sortOrder", "time"]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    return app.send_static_file("cjcx_cxXsXmcjList.html")


@app.route("/cjcx/cjcx_cxDgXscj.html", methods=["post"])
def score():
    _args = ["xnm", "xqm", "_search", "nd", "queryModel.showCount", "queryModel.currentPage",
             "queryModel.sortName", "queryModel.sortOrder", "time"]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    return app.send_static_file("cjcx_cxDgXscj.html")


@app.route("/kwgl/kscx_cxXsksxxIndex.html", methods=["post"])
def exam():
    _args = ["xnm", "xqm", "ksmcdmb_id", "kch", "kc", "ksrq", "kkbm_id", "_search", "nd", "queryModel.showCount",
             "queryModel.currentPage", "queryModel.sortName", "queryModel.sortOrder", "time"]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    return app.send_static_file("kscx_cxXsksxxIndex.html")


@app.route("/design/funcData_cxFuncDataList.html", methods=["post"])
def course_lib():
    _args = ["xnm", "xqm", "_search", "nd", "queryModel.showCount", "queryModel.currentPage", "queryModel.sortName",
             "queryModel.sortOrder"]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    if request.args.get("func_widget_guid", None) != "DA1B5BB30E1F4CB99D1F6F526537777B":
        return ""
    page = request.form.get("queryModel.currentPage")
    count = request.form.get("queryModel.showCount")
    print(count)
    if count == '1':
        return app.send_static_file("funcData_cxFuncDataList_initial.html")
    if count == '40':
        return app.send_static_file(f"funcData_cxFuncDataList_{page}.html")
    return ""


@app.route("/cjpmtj/gpapmtj_tjGpapmtj.html", methods=["post"])
def gpa_query():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    return app.send_static_file("gpapmtj_tjGpapmtj.html")
