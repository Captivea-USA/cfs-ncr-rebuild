# -*- coding: utf-8 -*-


{
    'name': "Cap Contact Card",

    'summary': """
        Mimic form view in UAT v14""",

    'description': """
        Import the custom contact fields from UAT add the tab D&B and Audit & Review in contact form
    """,

    'author': "Captivea",
    'website': "http://www.captivea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contact',
    'version': '15.0',

    # any module necessary for this one to work correctly
    # EOI 245: Added account_check_printing
    'depends': ["cfs_autoexec", 'base', 'contacts','purchase','cap_product_tag','cfs_product','account_check_printing','account','cap_report_migration'],

    # always loaded
    'data': [       
        'views/contact_form_view_inherit.xml',
        'views/contact_tree_view_inherit.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'license': 'LGPL-3',
    'application':False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
