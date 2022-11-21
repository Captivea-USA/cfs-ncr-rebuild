# -*- coding: utf-8 -*-
{
    'name': "CFS_Add_Bank_Accounts_Chatter",
    'summary': "Implements chatter on bank accounts view",
    'description': """
        Adds Chatter functionality to the Bank Accounts. Specifically the ability to:
        - Send Messages
        - Leave Log Notes
        - Attach Files
        - Follow Threads
    """,
    'author': "Commonwealth Fusion Systems",
    'website': "http://cfs.energy",
    'category': 'CFS',
    'version': '15.0',
    'depends': ["cfs_autoexec", 'base','contacts','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_partner_bank_form_inherit.xml',
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
