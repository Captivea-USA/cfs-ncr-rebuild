from odoo import fields, api, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # EOI-296: Add Custom Fields from UAT v14
    name = fields.Char(string="PO Number" )
    date_order = fields.Datetime(string="Release By", invisible=False)
    user_id = fields.Many2one(
            'res.users', string='Created By', index=True, tracking=True,
            default=lambda self: self.env.user, check_company=True)
    date_planned = fields.Datetime(
        string='Need Date', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

    # EOI-315: Removed purchase.order.line inheritance and cfs_custom_fields and moved into 'purchase_request' module

