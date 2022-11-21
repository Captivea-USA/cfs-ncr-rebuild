from odoo import models, fields, api


class ApprovalRequest(models.Model):

    _inherit = "approval.product.line"

    # EOI-322: Auto populate Buyer on Purchase Orders
    @api.onchange('product_id','buyer_category_id','cap_vendor_name')
    def _onchange_buyer(self):
        for rec in self:
            buyer_categ = rec.buyer_category_id
            if rec.product_id and rec.product_id.procurement_owner:
                rec.buyer_id = rec.product_id.procurement_owner.id
            elif rec.cap_vendor_name and rec.cap_vendor_name.buyer_id:
                rec.buyer_id = rec.cap_vendor_name.buyer_id
            elif buyer_categ:
                rec.buyer_id = buyer_categ[0].buyer_id
            else:
                rec.buyer_id = False

    # EOI-533: Remove description auto-poulation and add placeholder
    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(ApprovalRequest, self)._onchange_product_id()
        self.description = False