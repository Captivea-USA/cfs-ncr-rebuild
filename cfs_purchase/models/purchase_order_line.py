from odoo import models, fields, api
from datetime import datetime

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # EOI-400: Fix auto-population default tax id on PO order lines
    @api.onchange("product_id")
    def _compute_tax_id(self):
        super(PurchaseOrderLine, self)._compute_tax_id()
        if self.order_id.cfs_default_product_line_tax:
            self.taxes_id = self.order_id.cfs_default_product_line_tax

    def _add_chatter_changes(self,vals):
        """EOI530 - add chatter for certain changed fields
        need date
        promise date
        terms and conditions
        """
        ar = '<div title="Changed" role="img" class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right"/>'
        for line in self:
            msg = '<ul class="o_Message_trackingValues">'
            if not vals.get('sequence'):
                msg += f'Changes to line: {line.sequence} ({line.product_id.name})'
            else:
                msg += f'Line {line.sequence} ({line.product_id.name}) is now Line {vals.get("sequence")}'
            if vals.get('change_type'):
                msg += f"<li>Change: {line.change_type} {ar} {vals.get('change_type')}</li>"
            if vals.get('date_planned') == False or isinstance(vals.get('date_planned'), str):
                old_need_date = line.date_planned and fields.Date.to_date(line.date_planned) or False
                new_need_date = vals.get('date_planned') and fields.Date.to_date(vals.get('date_planned')).strftime('%m/%d/%y')
                msg += f"<li>Need Date: {old_need_date and old_need_date.strftime('%m/%d/%y')} {ar} {new_need_date}</li>"
            if vals.get('date_promised') == False or vals.get('date_promised'):
                new_promice_date = vals.get('date_promised') and fields.Date.to_date(vals.get('date_promised')).strftime('%m/%d/%y')
                msg += f"<li>Promise Date: {str(line.date_promised and line.date_promised.strftime('%m/%d/%y'))} {ar} {new_promice_date} </li>"
            line.order_id.message_post(body=msg)


    def write(self, vals):
        """EOI530: add chatter for tracked items
        """
        if 'change_type' in vals or 'date_planned' in vals or 'date_promised' in vals:
            self._add_chatter_changes(vals)
        return super().write(vals)