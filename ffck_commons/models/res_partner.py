# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv.expression import OR
from .ffck_structure_type import SCALES


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Partner fields
    ffck_network = fields.Boolean(string="FFCK network")
    first_membership_date = fields.Date("Structure 1st membership")
    # Structure typing
    partner_scale = fields.Selection(
        selection=SCALES,
        string="Scale",
        compute="_get_partner_scale",
        store=True,
    )
    ffck_structure_type_id = fields.Many2one(
        comodel_name="ffck.structure.type", string="Structure type"
    )
    partner_code = fields.Char(string="FFCK code", size=6, index=True)
    # partner_code_editable = fields.Boolean(string="FFCK code editable", compute="_can_edit_partner_code")
    # FFCK
    ffck_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="FFCK partner",
        ondelete="restrict",
        compute="_get_ffck_partner",
        store=False,
    )
    ffck_partner_code = fields.Char(string="FFCK", default="0", readonly=True)
    # CRCK
    crck_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="CRCK partner",
        index=True,
        ondelete="restrict",
        compute="_get_crck_partner",
        store=True,
    )
    crck_partner_code = fields.Char(related="crck_partner_id.partner_code", store=True)
    # CDCK
    cdck_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="CDCK partner",
        index=True,
        ondelete="restrict",
        compute="_get_cdck_partner",
        store=True,
    )
    cdck_partner_code = fields.Char(related="cdck_partner_id.partner_code", store=True)
    local_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Local partner",
        index=True,
        ondelete="restrict",
        domain=[("ffck_network", "=", True), ("partner_scale", "=", 4)],
    )
    local_partner_code = fields.Char(
        related="local_partner_id.partner_code", store=True
    )

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

    # COMPUTES

    @api.depends("company_type", "ffck_structure_type_id")
    def _get_partner_scale(self):
        for partner in self:
            if partner.company_type == "individual":
                partner.partner_scale = "5"
            else:
                partner.partner_scale = (
                    partner.ffck_structure_type_id
                    and partner.ffck_structure_type_id.scale
                )

    def _get_ffck_partner(self):
        ffck = self.env.ref("ffck_commons.res_partner_ffck", raise_if_not_found=False)
        main = self.env.ref("base.main_partner")
        for partner in self:
            if main.ref == "FFCK":
                if ffck and ffck.active:
                    ffck.write({"active": False})
                partner.ffck_partner_id = main
            else:
                partner.ffck_partner_id = ffck

    @api.depends("state_id", "ffck_network", "partner_scale")
    def _get_crck_partner(self):
        states = self.mapped("state_id")
        crck_ok = self.search(
            [
                ("ffck_network", "=", True),
                ("partner_scale", "=", "2"),
                ("state_id", "in", states.ids),
            ]
        )
        crck_by_state = {(crck.state_id, crck) for crck in crck_ok}
        states_ok = states - crck_ok.mapped("state_id")
        concerned = self.filtered(
            lambda rp: rp.ffck_network
            and int(rp.partner_scale) >= 3
            and rp.state_id in states_ok
        )
        for partner in concerned:
            state = partner.state_id
            partner.crck_partner_id = crck_by_state[state]
        # treat unconcerned
        for partner in self - concerned:
            partner.crck_partner_id = False

    @api.depends("country_department_id", "ffck_network", "partner_scale")
    def _get_cdck_partner(self):
        depts = self.mapped("country_department_id")
        cdck_ok = self.search(
            [
                ("ffck_network", "=", True),
                ("partner_scale", "=", "4"),
                ("country_department_id", "in", depts.ids),
            ]
        )
        cdck_by_dept = {(cdck.country_department_id, cdck) for cdck in cdck_ok}
        depts_ok = depts - cdck_ok.mapped("country_department_id")
        concerned = self.filtered(
            lambda rp: rp.ffck_network
            and int(rp.partner_scale) >= 4
            and rp.country_department_id in depts_ok
        )
        for partner in concerned:
            dept = partner.country_department_id
            partner.cdck_partner_id = cdck_by_dept[dept]
        # treat unconcerned
        for partner in self - concerned:
            partner.cdck_partner_id = False

    # ONCHANGES

    @api.onchange("partner_code", "company_type", "ffck_network")
    def onchange_partner_code(self):
        if self.ffck_network and self.is_company == False:
            code = self.partner_code
            if len(code) < 6:
                self.update({"partner_code": code.zfill(6)})
            elif len(code) > 6:
                self.update({"partner_code": code[:-6]})
