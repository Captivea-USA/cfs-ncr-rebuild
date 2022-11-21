{
    "name": "CFS Products",
    "author": "Commonwealth Fusion Systems",
    "website": "https://cfs.energy",
    "category": "Inventory/Purchase",
    "version": "15.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "summary": "CFS Product Master Fields to bring from v14 to v15",
    "description": "CFS Product Master Fields to bring from v14 to v15",
    "images": ["static/description/icon.png"],
    # mrp plm is needed for version on product.template
    "depends": ["cfs_autoexec", "sale","product", "mrp_plm", "sale_stock"],
    
    "data": [
        "security/ir.model.access.csv",
        # "security/res.groups.xml",
        "data/product.category.xml",
        "data/product.xml",
        "data/partner_data.xml",
        "views/product_product.xml",
        "views/product_template.xml",
        "views/commodity_code.xml",
        "views/product_category.xml",
        "views/quality_code.xml",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
