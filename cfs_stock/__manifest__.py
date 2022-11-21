# -*- coding: utf-8 -*-
{
    'name': "CFS Stock",

    'summary': """
        CFS custom override of stock related modules""",

    'description': """
        CFS custom override of stock related modules
    """,

    'author': "Odoo Inc.",
    'website': "http://www.odoo.com",
    'category': 'Inventory/Inventory',
    'license': 'OEEL-1',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        "views/stock_warehouse_views.xml",
        "views/stock_quants.xml",
        "views/stock_moves.xml"
    ],
}
