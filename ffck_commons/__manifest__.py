# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FFCK commons",
    "version": "1.0.0",
    "summary": "",
    "description": "",
    "author": "RemiFr82",
    "website": "https://remifr82.me",
    "license": "AGPL-3",
    "category": "Technical",
    "depends": [
        "base",
        "contacts",
        "l10n_fr_association",
        "partner_contact_age_range",
        "partner_contact_birthdate",
        "partner_contact_gender",
        "partner_contact_email2",
        "partner_contact_nationality",
        "partner_contact_personal_information_page",
        "partner_contact_phones2",
        "partner_firstname",
    ],
    "data": [
        # Base data
        "data/ffck_structure_type.xml",
        "data/res_partner.xml",
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/res_partner.xml",
        "views/ffck_structure_type.xml",
        # Wizards
        # 'wizards/ir_model_wizard.xml',
        # Reports
        # 'reports/report_assets.xml',
    ],
    # 'assets': {
    #     'web.report_assets_common': [
    #         'ffck_color_paddles/static/src/scss/report_pdf.scss',
    #     ],
    # },
    "demo": [],
    "auto_install": False,
    "external_dependencies": [],
    "application": True,
    "css": [],
    "images": [],
    "installable": True,
    "maintainer": "RemiFr82",
    "pre_init_hook": "",
    "post_init_hook": "",
    "uninstall_hook": "",
}
