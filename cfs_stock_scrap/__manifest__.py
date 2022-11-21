# -*- coding: utf-8 -*-
{
    'name': "CFS: MRB Location",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Task ID: 2503583
        The objective for this dev is for the user to create Helpdesk Tickets for materials that are non-confirming with Quality.
        User will use scrap function to send product to Non-Confirming Location
        Odoo will create return Picking
    """,

    'author': "Odoo Inc.",
    'website': "http://www.odoo.com",
    'category': 'Inventory/Inventory',
    'license': 'OEEL-1',
    'version': '0.1',
    'depends': ["cfs_autoexec", 'stock', 'helpdesk', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/picking_views.xml',
        'views/scrap_reason_views.xml',
        'views/scrap_views.xml',
        'views/stock_menu_views.xml',
        'views/ticket_views.xml',
        'data/helpdesk_team_data.xml',
        'data/scrap_reason_data.xml',
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
