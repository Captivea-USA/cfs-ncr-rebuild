# -- coding: utf-8 --
{
    "name": "CFS Purchase",
    "summary": "CFS modifications to purchase behavior",
    "description": "CFS modifications to Purchase behavior",
    "author": "Commonwealth Fusion Systems",
    "website": "https://www.cfs.energy/",
    "category": "Customizations/Purchase",
    "version": "15.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["static/description/icon.png"],
    "depends": ["cfs_autoexec", "purchase", "web", "cap_purchase_form_view", "cap_approvals"],
    "data": [
      "data/scheduled_actions.xml", 
      "views/purchase_order_views.xml",
      "wizard/mail_compose_form_views.xml"
    ],
    "assets": {
        "web.assets_backend": ["cfs_purchase/static/src/js/relational_fields.js"]
    },
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
