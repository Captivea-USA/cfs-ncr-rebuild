# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    "name": "Grant/Fund Project Analytic Budget Manage",
    "version": "2.1.2",
    "price": 9.0,
    "currency": "EUR",
    "category": "Accounting/Accounting",
    "license": "Other proprietary",
    "live_test_url": "https://probuseappdemo.com/probuse_apps/grant_fund_budget_manage_ent/211",  #'https://youtu.be/JhJhHREDzM8',
    "images": [
        "static/description/img.jpg",
    ],
    "summary": "Grants / fund projects with budget as grant seekers as well as grant makers.",
    "description": """
This app allows you to have management of your grants / fund projects with budget as grant seekers as well as grant makers.
    - Allow your grant / fund project team to create a project costing sheet for material, labour and overhead related to the projects of grant / fund seeking applications.
    - You can create a budget with selected ‘Grant Applications’ for grant seeking applications.
    - You can create a budget with selected ‘Grant Types’ for grant maker applications.
    - You can get more details about job costing sheet and material requisition in dependant apps by clicking links https://apps.odoo.com/apps/modules/14.0/odoo_job_costing_management/ and https://apps.odoo.com/apps/modules/14.0/material_purchase_requisitions/.
    - You can also get more details about the Grant/Fund depend app here https://apps.odoo.com/apps/modules/14.0/grant_fund_manage_odoo/.
    - For budget, you can check dependant app https://apps.odoo.com/apps/modules/14.0/job_costing_budget_contracting/.
    - For more details you can watch the video and check below screenshots.
    """,
    "author": "Probuse Consulting Service Pvt. Ltd.",
    "website": "www.probuse.com",
    "depends": [
        "cfs_autoexec", 
        "grant_fund_manage_odoo",
        "job_costing_budget_contracting_enterprice",
        #'timesheet_grid'
    ],
    "support": "contact@probuse.com",
    "data": [
        "views/crossovered_budget_view.xml",
        "views/grant_seeker_application_view.xml",
    ],
    "installable": True,
    "application": False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
