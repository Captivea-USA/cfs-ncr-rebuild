# -*- coding: utf-8 -*-
{
    'name': "Purchase Request Inheritance",

    'summary': """
        Inherit Purchase Order and adjust views""",

    'author': "Captivea USA",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ["cfs_autoexec", 'base', 'purchase', 'mrp', 'stock', 'account', 'cfs_purchase','cap_purchase_approval','cfs_product','multi_level_approval','cap_report_migration'],

    # always loaded
    'data': [
        'views/purchase_request_list_view.xml',
        'views/purchase_request_form_view.xml',
        'views/actions.xml',
        'views/menu.xml',
        'views/purchase_order_view_search_inherit.xml',
        'views/order_history_list_view.xml',
        'views/expanded_po_lines.xml',
    ],
    'assets': {
        'web.assets_qweb':[
            'purchase_request/static/src/xml/purchase_dashboard.xml',
        ],
    },
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
