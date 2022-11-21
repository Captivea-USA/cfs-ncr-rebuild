from odoo import api,fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # EOI-296: Change string from Shipping Method to Vendor Shipping
    cap_shipping_method = fields.Many2one('res.partner.shipping.method', string='Vendor Shipping')
    
    # EOI-428: 1b)Populate Vendor Shipping field from the vendor contact configuration(partner_id)
    # EOI-428: 7)Auto-populate Vendor Shipping, Incoterms, and Payment Terms fields from the vendor card upon vendor selection(partner_id)
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.cfs_shipping_method:
            self.cap_shipping_method = self.partner_id.cfs_shipping_method

        if self.partner_id.incoterms:
            self.incoterm_id = self.partner_id.incoterms

        if self.partner_id.property_supplier_payment_term_id:
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id
