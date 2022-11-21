from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ApprovalRequest(models.Model):

    _inherit = "approval.request"

    reason = fields.Text(required=True)

    # EOI-518: Fix RL/BQ menu domains
    purchase_order_count = fields.Integer(store=True)

    # EOI-322: Auto populate Buyer on Purchase Orders
    @api.model
    def create(self, vals):
        vals["cap_buyer_ids"] = []
        for line in vals["product_line_ids"]:
            if line[2] and line[2]["buyer_id"]:
                vals["cap_buyer_ids"].append(line[2]["buyer_id"])
            # vals["cap_buyer_ids"].append(line.buyer_id)
        vals["cap_buyer_ids"] = [(6, 0, set(vals["cap_buyer_ids"]))] 
        return super(ApprovalRequest, self).create(vals)

    # EOI-372: Warehouse onchange action events
    @api.onchange('cap_warehouse')
    def _onchange_warehouse(self):
        for rec in self:
            if rec.cap_warehouse.wh_type == 'production':
                rec.product_line_ids.write({'is_prod': True})
                # rec.product_line_ids._onchange_buyer()
            else:
                rec.product_line_ids.write({'is_prod': False})

    po_canceled = fields.Boolean(compute='_compute_po_cancelled')

    api.depends('purchase_order.state')
    def _compute_po_cancelled(self):
        """EOI377 - compute if the POs are canceled
        """
        for pr in self:
            pos = pr.product_line_ids.purchase_order_line_id.order_id
            pr.po_canceled = not pos.filtered(lambda po: po.state != 'cancel')
    
    # EOI-516 PR Submit button click action
    def action_confirm(self):
        approvers = self.mapped("approver_ids").filtered(
            lambda approver: approver.status == "new"
            and approver.user_id.id == self.request_owner_id.id
        )

        # Commented because we do no want activity chatter on PRs
        # approvers.sudo()._create_activity()
        approvers.write({"status": "pending"})

        # if self.res_model == "purchase.order":
        #     po = self.env["purchase.order"].browse(self.res_id)
        #     po.rejected = False

        self.sudo().with_context({"submit": 1}).write({'date_confirmed': fields.Datetime.now()})

        # if self.pr:
        if self.cap_type == 'new' and not self.product_line_ids:
            raise ValidationError('Please add products/items to your Purchase Request')
        # Commenting because on V14 it use to create Account Analytic Line
        # self.product_line_ids.generate_similar_buyer()
        # self.submit_request_action()
        self.write({'request_status': 'approved'})
