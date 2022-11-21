# -*- coding: utf-8 -*-
{
    'name': "CFS: Portal Bank Info",

    'summary': """
        To give opportunity to all portal users of a Vendor to be able to add and edit any Banking Information related to their Company""",

    'description': """
        Task ID: 2480404
    """,

    'author': "CFS/Odoo Inc.",
    'category': 'Website/Website',
    'license': 'OEEL-1',
    'version': '15.0',
    'depends': ['cfs_autoexec','portal', 'account_accountant', 'base_iban', 'l10n_us'],
    'data': [
        'data/ir_config_parameter.xml',
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'views/res_partner_bank_views.xml',
        'views/account_move_views.xml',
    ],
}
