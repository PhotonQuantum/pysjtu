from os import path

from flask import Flask, redirect, request, session

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
    if password == "1145141919810":
        return redirect("/jaccount/jalogin?err=0")
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
    if count == '1':
        return app.send_static_file("funcData_cxFuncDataList_initial.html")
    if count == '40':
        return app.send_static_file(f"funcData_cxFuncDataList_{page}.html")
    return ""


@app.route("/cjpmtj/gpapmtj_tjGpapmtj.html", methods=["post"])
def gpa_query():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.form.get("tjgx", None) != "1":
        return app.send_static_file("gpapmtj_tjGpapmtj_unauthorized.html")
    if request.form.get("kcfw", None) != "hxkc":
        return app.send_static_file("gpapmtj_tjGpapmtj_failure.html")
    session["is_gpa_calculated"] = True
    return app.send_static_file("gpapmtj_tjGpapmtj.html")


@app.route("/cjpmtj/gpapmtj_cxGpaxjfcxIndex.html", methods=["post"])
def gpa():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if not session.get("is_gpa_calculated", None):
        return ""
    return app.send_static_file("gpapmtj_cxGpaxjfcxIndex.html")


@app.route("/test_selection")
def enable_selection():
    session["enable_selection"] = True
    return "OK"


@app.route("/test_no_conflict")
def no_conflict():
    session["no_conflict"] = True
    return "OK"


@app.route("/test_no_full")
def no_full():
    session["no_full"] = True
    return "OK"


@app.route("/get_session")
def get_session():
    return str(session.get(request.args.get("key", ""), ""))


@app.route("/xsxk/zzxkyzb_cxZzxkYzbIndex.html", methods=["get"])
def selection_all_sectors():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.args.get("su", None) != SU:
        return ""
    if not session.get("enable_selection", None):
        return app.send_static_file("zzxkyzb_cxZzxkYzbIndex_not_selecting.html")
    session["query_all_sectors"] = session.get("query_all_sectors", 0) + 1
    return app.send_static_file("zzxkyzb_cxZzxkYzbIndex.html")


@app.route("/xsxk/zzxkyzb_cxZzxkYzbDisplay.html", methods=["post"])
def selection_sector_param():
    _args = ["xkkz_id", "xszxzt", "kspage", "jspage"]
    sectors = [
        "A000000000000B76E055F8163ED16360",
        "A000000000000A7FE055F8163ED16360",
        "A000000000000881E055F8163ED16360",
        "A000000000000F12E055F8163ED16360",
        "A000000000000455E055F8163ED16360",
        "A000000000000B28E055F8163ED16360"
    ]
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.args.get("su", None) != SU:
        return ""
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    if request.form["xkkz_id"] not in sectors or request.form["xszxzt"] != "1":
        return ""
    session["query_sector_param"] = session.get("query_sector_param", 0) + 1
    return app.send_static_file("zzxkyzb_cxZzxkYzbDisplay.html")


@app.route("/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html", methods=["post"])
def selection_query_courses():
    _args = ['rwlx', 'xkly', 'xqh_id', 'zyh_id', 'njdm_id', 'bh_id', 'tykczgxdcs', 'xkxnm', 'xkxqm', 'kklxdm', 'xslbdm',
             'ccdm', 'kklxdm', 'xbm', 'zyfx_id', 'xsbj', 'kkbk', 'sfkknj', 'sfkkzy', 'sfznkx', 'zdkxms', 'kspage',
             'jspage']
    _params = {
        "rwlx": "1",
        "xkly": "1",
        "kklxdm": "01"
    }
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.args.get("su", None) != SU:
        return ""
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    for k, v in _params.items():
        if request.form.get(k, None) != v:
            return ""
    session["query_courses"] = session.get("query_courses", 0) + 1
    return app.send_static_file("zzxkyzb_cxZzxkYzbPartDisplay.html")


@app.route("/xsxk/zzxkyzb_cxJxbWithKchZzxkYzb.html", methods=["post"])
def selection_query_classes():
    _args = ['rwlx', 'xkly', 'xqh_id', 'zyh_id', 'njdm_id', 'bh_id', 'tykczgxdcs', 'xkxnm', 'xkxqm', 'kklxdm', 'xslbdm',
             'ccdm', 'kklxdm', 'xbm', 'zyfx_id', 'xsbj', 'kkbk', 'sfkknj', 'sfkkzy', 'sfznkx', 'zdkxms', 'kch_id']
    _params = {
        "rwlx": "1",
        "xkly": "1",
        "kklxdm": "01",
        "kch_id": "CS241"
    }
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    if request.args.get("su", None) != SU:
        return ""
    for arg in _args:
        if arg not in request.form.keys():
            return ""
    for k, v in _params.items():
        if request.form.get(k, None) != v:
            return ""
    session["query_classes"] = session.get("query_classes", 0) + 1
    return app.send_static_file("zzxkyzb_cxJxbWithKchZzxkYzb.html")


@app.route("/xsxk/zzxkyzb_xkBcZyZzxkYzb.html", methods=["post"])
def selection_register():
    _params = {
        "jxb_ids": "0f40b5296313cee8407cc4d78b0f8e17a22dd66977e4b2eba40bfa7e9609a2af5655bd56084525b52eaccc0022135fd40796bc9a0bb7246d827b52abe9404552947bb23a54841d74982f19b9a3cdc3c96455efeeb8bdeaef5a90b5afdb06f81b83de2008ab1be401d9f4d2b0a42b570de845e82f6d15a2e03c3e5ec42ebdcf3d",
        "kch_id": "CS241",
        "qz": "0"
    }
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for k, v in _params.items():
        if request.form.get(k, None) != v:
            return '{"msg":"出现未知异常，请与管理员联系！","flag":"0"}'
    if not session.get("no_conflict", False):
        return '{"msg": "所选教学班的上课时间与其他教学班有冲突！","flag":"0"}'
    if not session.get("no_full", False):
        return '{"msg":"1,A0000000000020C2E055F8163ED16360,80","flag":"-1"}'
    session["registered"] = True
    return '{"flag":"1"}'


@app.route("/xsxk/zzxkyzb_tuikBcZzxkYzb.html", methods=["post"])
def selection_deregister():
    _params = {
        "kch_id": "CS241",
        "jxb_ids": "0f40b5296313cee8407cc4d78b0f8e17a22dd66977e4b2eba40bfa7e9609a2af5655bd56084525b52eaccc0022135fd40796bc9a0bb7246d827b52abe9404552947bb23a54841d74982f19b9a3cdc3c96455efeeb8bdeaef5a90b5afdb06f81b83de2008ab1be401d9f4d2b0a42b570de845e82f6d15a2e03c3e5ec42ebdcf3d"
    }
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for k, v in _params.items():
        if request.form.get(k, None) != v:
            return '"3"'
    session["registered"] = False
    return '"1"'


@app.route("/xsxk/zzxkyzb_xkJcInXksjZzxkYzb.html", methods=["post"])
def selection_is_registered():
    _params = {
        "jxb_id": "0f40b5296313cee8407cc4d78b0f8e17a22dd66977e4b2eba40bfa7e9609a2af5655bd56084525b52eaccc0022135fd40796bc9a0bb7246d827b52abe9404552947bb23a54841d74982f19b9a3cdc3c96455efeeb8bdeaef5a90b5afdb06f81b83de2008ab1be401d9f4d2b0a42b570de845e82f6d15a2e03c3e5ec42ebdcf3d",
        "xkkz_id": "A000000000000B76E055F8163ED16360",
        "xnm": "2020",
        "xqm": "3"
    }
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    for k, v in _params.items():
        if request.form.get(k, None) != v:
            return '"0"'
    return '"1"' if session.get("registered", False) else '"0"'

@app.route("/xsxxxggl/xsgrxxwh_cxXsgrxx.html", methods=["get"])
def profile():
    if not session.get("is_login", None):
        return redirect("/xtgl/login_slogin.html")
    _args = {
        "gnmkdm": "N100801"
    }
    if request.args.get("su", None) != SU:
        return ""
    for k, v in _args.items():
        if request.args.get(k, None) != v:
            return ""
    session["query_profile"] = session.get("query_profile", 0) + 1
    return app.send_static_file("xsgrxxwh_cxXsgrxx.html")