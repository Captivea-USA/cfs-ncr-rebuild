# -*- coding: utf-8 -*-
######################################################################################
#
#    Captivea LLC
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('revised', 'Revised')])
    active = fields.Boolean(default=True)
    po_is_revision = fields.Boolean('Is Revised PO', readonly=True)
    prior_po = fields.Many2one("purchase.order", string="Prior PO", readonly=True,)

    def button_revise_po(self):
        # EOI-520: Revise PO Logic
        for record in self:
            # Add name from previous PO to new revision PO (ord_name = record.name)
            original_order = record.name
            # Create Copy of Original PO
            new_po = record.copy(default=None)
            sequence = self.env['ir.sequence'].search([('code','=','purchase.order')])
            sequence['number_next_actual']=sequence.number_next_actual - 1

            # Adjust original PO data with the new PO
            new_po.write({
                'name': original_order,
                'state': 'revised',
                'is_editable': False,
                'message_ids': record.message_ids,
                "date_approve": False,
            })
            record.date_approve = False
            new_id = new_po.id
            record.prior_po = new_id

            # Find all linked PRs using the orig PO and point to the new one
            change_orders = self.env['multi.approval'].search([
                ("purchase_id", "=", record.id)
            ])
            for order in change_orders:
                # Cancel Approvals
                if order.state == 'Approved':
                    order.write({'state': 'Cancel'})

            # Add details to the PO chatter
            body = 'Created from <a href="#" data-oe-model="purchase.order" data-oe-id="%s">%s</a>' % \
                (str(record.id), original_order)
            record.message_post(body=body)
            record.state = 'to reapprove'
            # record.is_editable = True

            #EOI 321 - PO Revision Routing
            #EOI 323 - Prior PO Logic
            record.x_review_result = False
            record.x_has_request_approval = False

            #EOI 324 - Old q and $ logic
            record.po_is_revision = True

            # EOI497 set editable for the PO that will be created as a duplicate
            new_po.is_editable = False

            # Update data for Old PO
            for po_line in record.order_line:
                old_po_lines = record.order_line.filtered(lambda x: x.product_id == po_line.product_id )
                # EOI674 iterate through old purchase lines to avoid singleton errors
                for old_po_line in old_po_lines:
                    po_line.prior_product_qty = old_po_line.product_qty
                    po_line.prior_price_unit = old_po_line.price_unit
                    po_line.prior_line = True

            if str('-') in original_order:
                record.name = original_order[:original_order.rindex('-')] + str('-') + \
                           str(int(original_order[original_order.rindex('-')+1:])+1).zfill(3)
            else:
                record.name = original_order + '-001'

            # Adjustment of Pickings/Receipts wrt revised PO
            for transfer in record.picking_ids:
                transfer.origin = record.name

            # EOI497 - set editable for the new po
            record.is_editable = True

            form_id = self.env.ref('purchase.purchase_order_form', False).id
            result = {
                'name' : 'Purchase Order',
                'type' : 'ir.actions.act_window',
                'view_mode' : 'form',
                'res_model' : 'purchase.order',
                'view_id' : form_id,
                'target' : 'current',
                'res_id' : self.id
                #'res_id' : new_po.id
                }
            return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #EOI 324 - Old q and $ logic
    prior_product_qty = fields.Float(string="Old Q", readonly=True )
    prior_price_unit = fields.Float(string='Old $', readonly=True)
    prior_line = fields.Boolean(string="Old Line", readonly=True)
    change_type = fields.Selection([
        ('new', 'New'), 
        ('delete', 'Delete'), 
        ('price', 'Price'),
        ('qty', 'Qty'),
        ('price_qty', 'Price + Qty'),
    ],compute='_compute_change_type')

    #EOI 324 - Old q and $ logic
    @api.depends('prior_product_qty', 'prior_price_unit', 'prior_line')
    def _compute_change_type(self):
        for record in self:
            if not record.prior_line:
                record.change_type = 'new'
            elif record.prior_product_qty != record.product_qty and record.prior_price_unit != record.price_unit:
                record.change_type = 'price_qty'
            elif record.prior_product_qty != record.product_qty:
                record.change_type = 'qty'
            elif record.prior_price_unit != record.price_unit:
                record.change_type = 'price'
            else:
                record.change_type = False

    # EOI-535 Unit Price Updating when changing Quantity
    #we don't want pricing to auto change on a PO undergoing revision
    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.order_id.prior_po:
            super(PurchaseOrderLine, self)._onchange_quantity()

    # EOI-535 Unit Price Updating when changing Quantity
    # rewrite the function so it won't reset the price_unit when quantity is changed
    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # If not seller, use the standard price. It needs a proper currency conversion.
        if self.price_unit == 0:
            if not seller:
                po_line_uom = self.product_uom or self.product_id.uom_po_id
                price_unit = self.env['account.tax']._fix_tax_included_price_company(
                    self.product_id.uom_id._compute_price(self.product_id.standard_price, po_line_uom),
                    self.product_id.supplier_taxes_id,
                    self.taxes_id,
                    self.company_id,
                )
                if price_unit and self.order_id.currency_id and self.order_id.company_id.currency_id != self.order_id.currency_id:
                    price_unit = self.order_id.company_id.currency_id._convert(
                        price_unit,
                        self.order_id.currency_id,
                        self.order_id.company_id,
                        self.date_order or fields.Date.today(),
                    )

                self.price_unit = price_unit
                return

            price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
            if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
                price_unit = seller.currency_id._convert(
                    price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

            if seller and self.product_uom and seller.product_uom != self.product_uom:
                price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

            self.price_unit = price_unit

    def write(self, vals):
        # EOI-520: Revise PO Logic
        # Update Picking Product Qty when updated for the Revised PO
        res = super().write(vals)
        lines = self.filtered(lambda l: l.order_id.state == 'to reapprove')
        previous_product_qty = {line.id: line.product_uom_qty for line in lines}
        if 'product_qty' in vals:
            lines.with_context(previous_product_qty=previous_product_qty)._create_or_update_picking()
        return res
