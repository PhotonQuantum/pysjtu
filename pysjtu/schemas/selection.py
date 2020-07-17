from marshmallow import Schema, fields, post_load  # type: ignore


class SelectionSharedInfoSchema(Schema):
    term = fields.Str(required=True, data_key="xqh_id")
    selection_year = fields.Int(required=True, data_key="xkxnm")
    selection_term = fields.Int(required=True, data_key="xkxqm")
    major_id = fields.Str(required=True, data_key="zyh_id")
    student_grade = fields.Int(required=True, data_key="njdm_id")
    natural_class_id = fields.Str(required=True, data_key="bh_id")
    self_selecting_status = fields.Int(required=True, data_key="xszxzt")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return SelectionSharedInfo(**data)


class SelectionSectorSchema(Schema):
    task_type = fields.Int(required=True, data_key="rwlx")
    xkly = fields.Int(required=True)
    pe_op_param = fields.Int(required=True, data_key="tykczgxdcs")
    sector_type_id = fields.Str(required=True, data_key="bklx_id")
    course_type_code = fields.Int(required=True, dump_only=True, data_key="kklxdm")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return SelectionSector(**data)


from pysjtu.models.selection import SelectionSharedInfo, SelectionSector
