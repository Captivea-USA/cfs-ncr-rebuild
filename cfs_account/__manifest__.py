{
    "name": "CFS Account",
    "author": "Commonwealth Fusion Systems",
    "website": "https://cfs.energy",
    "category": "Accounting/Accounting",
    "version": "15.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "summary": "CFS modifications to the Account module",
    "description": "CFS modifications to the Account module",
    "images": ["static/description/icon.png"],
    # cybrosys blog says we need contacts
    "depends": ["cfs_autoexec", "account", "mail", "contacts", "l10n_us_payment_nacha"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/emails.xml",
        "views/bank_views.xml",
        "views/res_partner_views.xml",
        "views/payment.xml",
        "views/account_move.xml",
        "views/journal.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
