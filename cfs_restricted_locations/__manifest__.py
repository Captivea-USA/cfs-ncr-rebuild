# -*- coding: utf-8 -*-

{
    'name': "CFS Restricted Locations",

    'summary': """
        Enable configuration on locations to make them restricted, a restricted location can only receive the same product and the same lot number that already has""",

    'description': """
        Make posible set location as Restricted locations, and check that every line in the stock_picking can be done properly checking the constrains on the restricted 
        locations
    """,

    'author': "Captivea LLC",
    'website': "http://www.captivea.com",

    'category': 'Inventory',
    'version': '15.0',

    'depends': ["cfs_autoexec", 'base', 'base_automation', 'stock'],

    'data': [
        'views/stock_location.xml',
        'views/stock_warehouse_view.xml',
        'views/validation_on_safe.xml',
        'views/stock_putaway_tree_view_inherit.xml',
        ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively

}
