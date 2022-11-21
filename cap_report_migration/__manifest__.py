{
    "name": "Captivea CFS Report Migration",
    "summary": "Brings custom CFS Reports into Odoo v15",
    "description": """Adds the following reports: Delivery Slip, Draft Purchase Order,
    Forecasted Report, Purhcase Order, Return Receipt, Price-lists, Internal Report,
    Picking Operations, and Routes Report.""",
    "author": "Captivea",
    "category": "Purchase",
    "version": "15.0",
    "license": "AGPL-3",
    "depends": ["cfs_autoexec", "base","product","delivery","cap_purchase_form_view","approvals","stock","stock_account","purchase_stock","purchase"],
    "data": [
        "views/stock_views.xml",
        # "views/purchase_view.xml",
        "views/test_picking_type.xml",
        "report/delivery_slip.xml",
        "report/request_for_quotation.xml",
        "report/purchase_order.xml",
        "report/return_receipt.xml",
        "security/ir.model.access.csv",
    ],
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
