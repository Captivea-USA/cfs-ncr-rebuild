# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Remittance Advice Report",
    "author": "OMAX Informatics",
    "version": "15.0.1.0",
    "website": "https://www.omaxinformatics.com",
    "category": "Accounting,Finance,Purchases,Accounting & Finance",
    "description": """
        This app generate to Remittance Advice Report and set 'Remittance Advice: Send by email' template in 'Send receipt by email' popup in Vendor Payment.
    """,
    "summary": """
        Print and Send Remmitance Advice report,
        Remittance Advice,
        Remittance Advice report,
        Purchase Remmitance Advice,
        Vendor Bill Remittance Advice,
        Email Remmitance Advice,
        Send Remmitance Advice,
        Purchase Remmitance Advice Report,
        Vendor Bill Remittance Advice Report,
        Email Remmitance Advice Report,
        Send Remmitance Advice Report,

	""",
    "depends": ["cfs_autoexec", "account", "mail", "base"],
    "data": [
        "report/report_account_payment_menu.xml",
        "data/mail_template_data.xml",
        "report/report_layout.xml",
        "report/report_remittance_advice_tmpl_id.xml",
        "wizard/mail_compose_message_views.xml",
        "views/res_company.xml",
    ],
    "demo": [],
    "test": [],
    "images": [
        "static/description/banner.png",
    ],
    "license": "AGPL-3",
    "currency": "USD",
    "price": 42.0,
    "installable": True,
    "auto_install": False,
    "application": True,
    "pre_init_hook": "pre_init_check",
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
