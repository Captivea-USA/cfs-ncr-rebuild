from odoo import api,fields, models
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    cap_m2o_approval_product_line = fields.Many2one('approval.product.line', string='Approval Product Line')
    # cap_vendor_part = fields.Char(string="Vendor Part")

    cap_free_description = fields.Char(string='Description')
    # Removed CAP custom field as it's a duplication with different field type
    # cap_quality_codes = fields.Many2one('quality.code', string='Quality Code')
    cap_date_req = fields.Date(string='Requested Date')
    cap_taxable = fields.Boolean(string='Taxable')
