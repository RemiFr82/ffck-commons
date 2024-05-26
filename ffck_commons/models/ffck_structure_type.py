# -*- coding: utf-8 -*-
from odoo import models, fields
from .res_partner import SCALES


class FfckStructureType(models.Model):
    _name = "ffck.structure.type"
    _description = "FFCK structure type"

    name = fields.Char("Name", required=True)
    short = fields.Char("Short", required=True, index=True)
    scale = fields.Selection(SCALES, string="Scale", required=True)
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one(comodel_name="ffck.structure.type", string="Parent")
