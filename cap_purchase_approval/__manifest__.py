{
    "name": "Captivea CFS Purchase Approval Category",
    "summary": "Purchase Module now directs to approval.category view/model",
    "description": """Opens Approval.category in Purchase""",
    "author": "Captivea",
    "category": "Purchase",
    "version": "15.0",
    "license": "AGPL-3",
    "depends": ["cfs_autoexec", "base","approvals","purchase_stock","purchase","cfs_product","cap_report_migration",],
    "data": [
        "views/draft_po_list_view.xml",
        'data/approval_category_data.xml',
        "views/approval_category_kanban.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}