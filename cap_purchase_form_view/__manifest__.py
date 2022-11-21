{
    "name": "CFS Purchase Form View",
    "summary": "Edits New Request Form View in Purchasing",
    "description": "Adds and removes fields per CFS requirements",
    "author": "Captivea",
    "category": "Purchase",
    "version": "15.0",
    "license": "AGPL-3",
    # EOI460 - hr_expense is needed for a domain for product_filter_ids
    "depends": [
        "cfs_autoexec", "base","purchase","approvals","stock","multi_level_approval",
        "cfs_stock", "cfs_product","cap_product_tag","hr_expense", 'cap_approvals'],
    "data": [
        "data/stock.warehouse.xml",
        "views/approval_request_form_inherit.xml",
        "views/approval_product_line_inherit.xml",
        "views/approval_request_tree_inherit.xml",
        "views/expanded_approval_product_line.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}