# -*- coding: utf-8 -*-
from odoo import models, fields

SCALES = [
    ("1", "National"),
    ("2", "Regional"),
    ("3", "Departmental"),
    ("4", "Local"),
    ("5", "Licensee"),
]


class FfckStructureType(models.Model):
    _name = "ffck.structure.type"
    _description = "FFCK structure type"
    _order = "scale, short, name, id"

    name = fields.Char("Name", required=True, translate=True)
    short = fields.Char("Short", required=True, index=True)
    scale = fields.Selection(SCALES, string="Scale", required=True)
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one(comodel_name="ffck.structure.type", string="Parent")
