# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    "name": "Grant / Fund Management using CRM",
    "version": "4.1.3",
    "price": 99.0,
    "currency": "EUR",
    "category": "Sales/CRM",
    "license": "Other proprietary",
    "live_test_url": "https://probuseappdemo.com/probuse_apps/grant_fund_manage_odoo/824",  #'https://youtu.be/4pAEpIRLw6w',
    "images": [
        "static/description/img.jpg",
    ],
    "summary": "Management of grants / funds as grant seekers as well as grant makers using CRM.",
    "description": """
grant management
grant seeker
grant maker
grant
fund managment
project fund
fund app
grant management app
    """,
    "author": "Probuse Consulting Service Pvt. Ltd.",
    "website": "www.probuse.com",
    "depends": [
        "cfs_autoexec", 
        "crm",
        "mail",
        "project",
        "sales_team",
        "project_team_odoo",
        "purchase",
        "sale_management",
        "sale_crm",
    ],
    "support": "contact@probuse.com",
    "data": [
        "security/grant_application_security.xml",
        "security/ir.model.access.csv",
        "wizard/custom_grant_opportunity_wizard_view.xml",
        "wizard/custom_grant_project_wizard_view.xml",
        "report/grant_seeker_application_report_template.xml",
        "report/grant_seeker_application_report_lead_template.xml",
        "report/grant_seeker_application_report.xml",
        "views/crm_lead_view.xml",
        "views/grant_stages_view.xml",
        "views/grant_seeker_application_view.xml",
        "views/project_view.xml",
        "views/grant_types_view.xml",
        "views/grant_methods_view.xml",
        "views/grant_tags_view.xml",
        "views/purchase_view.xml",
        "views/sale_order_view.xml",
        "views/invoice_view.xml",
        "data/mail_data.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
