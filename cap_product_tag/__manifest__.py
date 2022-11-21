# -*- coding: utf-8 -*-

{
    'name': "Cap Product Tag",

    'summary': """
        Add product.tag model and Buyers category view""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Captivea",
    'website': "http://www.captivea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ["cfs_autoexec", 'base', 'purchase'],

    # always loaded
    'data': [
        'views/buyer.xml',
        'views/purchase.xml',
        
    ],
    'installable': True,
    'license': 'LGPL-3',
    'application':False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}