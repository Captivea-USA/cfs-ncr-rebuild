# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality Captivea',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'sequence': 50,
    'summary': 'Customization to Quality module',
    'depends': ['cfs_product','purchase','purchase_request','quality','quality_control'],
    'description': """
Quality 
===============
""",
    'data': [
        'views/quality_point.xml'
    ],
    'demo': [],
    'application': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [

        ],
        'web.assets_qweb': [

        ],
    }
}
