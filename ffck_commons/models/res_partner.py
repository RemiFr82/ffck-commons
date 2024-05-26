# -*- coding: utf-8 -*-
from odoo import models, fields, api

SCALES = [
    ("nat", "National"),
    ("reg", "Regional"),
    ("dep", "Departmental"),
    ("loc", "Local"),
    ("lic", "Licensee"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_ffck_partner(self):
        ffck = self.env.ref("ffck_commons.res_partner_ffck", raise_if_not_found=False)
        main = self.env.ref("base.main_partner")
        if main.ref == "FFCK":
            if ffck.active:
                ffck.write({"active": False})
            return main
        else:
            return ffck

    # Partner fields
    ffck_network = fields.Boolean(string="FFCK network")
    first_membership_date = fields.Date("Structure 1st membership")
    # Structure typing
    partner_scale = fields.Selection(
        selection=SCALES,
        string="Scale",
    )
    ffck_structure_type_id = fields.Many2one(
        comodel_name="ffck.structure.type", string="Structure type"
    )
    partner_code = fields.Char(string="FFCK code", size=6, index=True)
    # partner_code_editable = fields.Boolean(string="FFCK code editable", compute="_can_edit_partner_code")
    # FFCK
    ffck_partner_id = fields.Many2one(
        "res.partner",
        string="FFCK partner",
        default=_get_ffck_partner,
        ondelete="restrict",
    )
    ffck_partner_code = fields.Char(string="FFCK", default="0", readonly=True)
    # CRCK
    crck_partner_id = fields.Many2one(
        "res.partner",
        string="CRCK partner",
        index=True,
        ondelete="restrict",
    )
    crck_partner_code = fields.Char(related="crck_partner_id.partner_code", store=True)
    # CDCK
    cdck_partner_id = fields.Many2one(
        "res.partner",
        string="CDCK partner",
        index=True,
        ondelete="restrict",
    )
    cdck_partner_code = fields.Char(related="cdck_partner_id.partner_code", store=True)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Allow searching by sequence code by default."""
        # Do not add any domain when user just clicked on search widget
        if not (name == "" and operator == "ilike"):
            # The dangling | is needed to combine with the domain added by super()
            args = OR(
                [
                    [
                        "&",
                        ("ffck_network", "=", True),
                        ("partner_code", "=like", name + "%"),
                    ],
                    args or [],
                ]
            )
        return super().name_search(name, args, operator, limit)

    def name_get(self):
        result = []
        # ffck_partners = self.filtered('ffck_network')
        # others = self - ffck_partners
        for record in self:
            if record.ffck_network:
                code = record.partner_code
                ref = record.ref
                result.append(
                    (
                        record.id,
                        "{}{}{}".format(
                            code and code + " - " or "",
                            ref and record.is_company and ref + " - " or "",
                            super(ResPartner, record).name_get()[0][1],
                        ),
                    )
                )
            else:
                result += super(ResPartner, record).name_get()
        return result

    # ONCHANGES

    @api.onchange("partner_code", "company_type", "ffck_network")
    def onchange_partner_code(self):
        if self.ffck_network and self.company_type == "individual":
            code = self.partner_code
            if len(code) < 6:
                self.update({"partner_code": code.zfill(6)})
            elif len(code) > 6:
                self.update({"partner_code": code[:-6]})

    @api.onchange("company_type", "partner_scale", "ffck_structure_type_id")
    def onchange_comp_type(self):
        if self.company_type == "individual":
            self.update({"partner_scale": "lic"})
        elif self.partner_scale == "lic":
            self.update({"partner_scale": False})
        elif self.ffck_structure_type_id:
            self.update({"partner_scale": self.ffck_structure_type_id.scale})
