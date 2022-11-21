# -*- coding: utf-8 -*-
{
    'name': 'Odoo Approval',
    'version': '15.0.1.1',
    'category': 'Approvals',
    'description': """
Odoo Approval Module: Multi level approval - create and validate approvals requests.
Each request can be approve by many levels of different managers.
The managers wil review and approve sequentially
    """,
    'summary': '''
    Create and validate approval requests. Each request can be approved by many levels of different managers
    ''',
    'live_test_url': 'https://demo15.domiup.com',
    'author': 'Domiup',
    'price': 60,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://youtu.be/PJ7lTUn-qes',
    'depends': [
        "cfs_autoexec", 
        'mail',
        'product',
        'purchase', 
        'approvals'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        # wizard
        'wizard/refused_reason_views.xml',
        'wizard/confirm_dialog.xml',
        'views/multi_approval_type_views.xml',
        'views/multi_approval_views.xml',
        'views/multi_approval_view_form_inherit.xml',
        'views/multi_approval_smart_button.xml',

        # Add actions after all views.
        'views/actions.xml',

        # Add menu after actions.
        'views/menu.xml',
        
    ],
    'assets': {
        'web.assets_qweb': ["multi_level_approval/static/src/components/approval/approval.xml"],
    },
    'images': ['static/description/banner.jpg'],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
