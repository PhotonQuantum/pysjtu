from datetime import datetime

from pysjtu.models.base import Gender
from pysjtu.parser.profile import ProfileField

# @formatter:off
profile_fields = [
    ProfileField("student_id",              "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[1]/div/div/p", int),
    ProfileField("name",                    "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[2]/div/div/p"),
    ProfileField("name_pinyin",             "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/p"),
    ProfileField("former_name",             "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[4]/div/div/p"),
    ProfileField("gender",                  "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[5]/div/div/p", lambda x: Gender.male if x == "男" else Gender.female),
    ProfileField("certificate_type",        "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[6]/div/div/p"),
    ProfileField("certificate_number",      "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[7]/div/div/p", int),
    ProfileField("birth_date",              "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[4]/div/div/p", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    ProfileField("enrollment_date",         "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[8]/div/div/p", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    ProfileField("birthplace",              "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[12]/div/div/p"),
    ProfileField("ethnicity",               "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[5]/div/div/p"),
    ProfileField("native_place",            "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[9]/div/div/p"),
    ProfileField("foreign_status",          "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[13]/div/div/p"),
    ProfileField("political_status",        "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[7]/div/div/p"),
    ProfileField("enrollment_province",     "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[11]/div/div/p"),
    ProfileField("nationality",             "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[14]/div/div/p"),
    ProfileField("domicile_place",          "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[1]/div/div[10]/div/div/p"),
    ProfileField("cee_candidate_number",    "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[3]/div/div[1]/div/div/p", int),
    ProfileField("middle_school",           "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/p"),
    ProfileField("religion",                "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[3]/div/div[5]/div/div/p"),
    ProfileField("email",                   "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[1]/div/div/p"),
    ProfileField("cellphone",               "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[2]/div/div/p", int),
    ProfileField("family_address",          "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/p"),
    ProfileField("mailing_address",         "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[4]/div/div/p"),
    ProfileField("landline",                "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[5]/div/div/p", int),
    ProfileField("zip_code",                "/html/body/div[1]/div/div/form/div/div[2]/div/div/div/div/div[4]/div/div[6]/div/div/p", int)
]
# @formatter:on
