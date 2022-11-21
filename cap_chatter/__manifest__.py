# -*- coding: utf-8 -*-
{
    
    'name': "CFS Chatter",
    'summary': "Implements Chatter into views, and also edits the button strings",
    'description': """
        Adds Chatter functionality to the Bank Accounts. Specifically the ability to:
        - Send Messages
        - Leave Log Notes
        - Attach Files
        - Follow Threads
        Also changes the 'Send Message' and 'Log Note' strings to 'External Email' and 'Internal Note'
    """,
    'author': "Commonwealth Fusion Systems",
    'website': "http://cfs.energy",
    'category': 'CFS',
    'version': '15.0',
    'depends': ["cfs_autoexec", 'base','contacts','mail'],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
    'data': [
        'security/ir.model.access.csv',
        'views/view_partner_bank_form_inherit.xml',
        'views/certification_type.xml',
    ],
    'assets': {
        'web.assets_qweb':[
            'cap_chatter/static/src/xml/*.xml',
        ],
    }
}
