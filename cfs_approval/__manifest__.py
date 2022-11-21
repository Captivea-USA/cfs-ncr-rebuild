{
    "name": "CFS Approval",
    "author": "Commonwealth Fusion Systems",
    "website": "https://cfs.energy",
    "category": "Customizations/Approvals",
    "version": "15.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "summary": "CFS modifications to the Approvals module",
    "description": "CFS modifications to the Approvals module",
    "images": ["static/description/icon.png"],
    "depends": ["cfs_autoexec", "approvals", "cap_purchase_form_view", "purchase_request"],
    "data": [
        "views/approval_category.xml",
        "views/approval_request.xml",
        "views/purchase.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}