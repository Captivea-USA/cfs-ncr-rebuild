{
    "name": "CFS Exports",
    "author": "Commwealth Fusion Systems",
    "website": "https://cfs.energy",
    "category": "Inventory/Purchase",
    "version": "1.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "summary": "CFS exports for reporting purposes",
    "description": "CFS exports for reporting purposes",
    "images": ["static/description/icon.png"],
    # purchase is needed because the models are used in testing
    "depends": ["cfs_autoexec", "base", "purchase"],
    "data": [
        "data/scheduled_actions.xml",
        "data/ir_config_parameter.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
