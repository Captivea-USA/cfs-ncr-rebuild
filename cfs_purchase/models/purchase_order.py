from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # EOI-322: Auto populate Buyer on Purchase Orders
    cfs_buyer = fields.Many2one('res.users', string='Buyer', default=lambda self: self.env.user)

    def _check_close(self):
        purchase_orders = self.env["purchase.order"].search(
            [("state", "!=", "closed"), ("invoice_status", "=", "invoiced")]
        )
        for purchase_order in purchase_orders:
            for purchase_order_line in purchase_order.order_line:
                if purchase_order_line.qty_received != purchase_order_line.qty_invoiced:
                    continue
            active_invoices = []
            for invoice in purchase_order.invoice_ids:
                if invoice.state != "cancel":
                    active_invoices.append(invoice)
                open_invoices = (
                    True
                    if any(
                        invoice.state != "posted"
                        or invoice.payment_state not in ["in_payment", "paid"]
                        for invoice in active_invoices
                    )
                    else False
                )
            if open_invoices:
                continue
            if purchase_order.picking_ids:
                open_receipts = (
                    True
                    if any(
                        picking.state not in ["done", "cancel"]
                        for picking in purchase_order.picking_ids
                    )
                    else False
                )
                if open_receipts:
                    continue
            purchase_order.state = "closed"
        return True

    # EOI-400: Fix auto-population default tax id on PO order lines 
    @api.onchange('cfs_default_product_line_tax')
    def onchange_cfs_default_product_line_tax(self):
        if self.cfs_default_product_line_tax:
            for line in self.order_line:
                line.taxes_id = self.cfs_default_product_line_tax

    # EOI-372: Warehouse onchange action events
    @api.onchange('wh_type')
    def _onchange_warehouse_type(self):
        for rec in self:
            if rec.wh_type == 'production':
                rec.order_line.write({'is_prod':True})
                rec.order_line._update_quality_code()
            else:
                rec.order_line.write({'is_prod':False})

    # EOI-384: Add PO state change notifications(emails)
    def write(self, vals):
        old_state = self.state
        res = super().write(vals)
        vals_state = vals.get("state", False)
        if vals_state and vals_state != old_state and (self.cfs_buyer.login or self.requester_id.login):
            partner_ids = [self.cfs_buyer.partner_id.id, self.requester_id.partner_id.id]
            self.message_notify(
                subject=f"Status Updated: {self.name}",
                body=f"The status of {self.name} has been updated from {dict(self._fields['state'].selection).get(old_state)} --> {dict(self._fields['state'].selection).get(vals_state)}",
                partner_ids=partner_ids,
                record_name=self.display_name,
                email_layout_xmlid="mail.mail_notification_light",
                model_description=self.env["ir.model"]._get(self._name).display_name,
            )
        return res