# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # EOI-296: Add Custom Fields from UAT v14
    name = fields.Char(string="PO Number" )
    # EOI-356: Updated 'picking_type_id' to be required + added approval_request_id
    picking_type_id = fields.Many2one("stock.picking.type", string="Deliver To", required=True)
    approval_request_id = fields.Many2one('approval.request',string="Approval Request")

    date_order = fields.Datetime(string="Release By", invisible=False)

    # EOI-353: Need to add Text field above terms and conditions
    cap_po_notes = fields.Text('Additional Terms and Conditions', tracking=1)

    # EOI353 - override field to add text
    notes = fields.Html("Terms and Conditions", default="Unless otherwise agreed in a mutually accepted contract and referenced on this purchase order above, CFS Standard Terms and Conditions apply to this order - https://www.cfs.energy/legal/potnc - all invoices must be submitted electronically to ap@cfs.energy for payment processing.")

    cfs_released_by = fields.Many2one("res.users", string="Released By", required=False, )
    cfs_is_transfer_return = fields.Boolean(string="Transfer Return?",)
    cfs_approval_request = fields.Many2one(comodel_name="multi.approval", string="Approval Request", required=False, )
    cfs_approval_state = fields.Char(string="Approval State", compute='compute_state')
    cfs_default_product_line_tax = fields.Many2many('account.tax',string="Default Product Taxes")
    cfs_rejected = fields.Boolean(string="Rejected")

    # EOI-341/512: Added requester_id since it's needed in order_line
    requester_id = fields.Many2one(string='Requester', comodel_name='res.users', default= lambda self: self.env.user)

    date_approve = fields.Datetime(string='Approved on',)
    # Commenting it because field already added above on line 17 (duplication)
    # approval_request_id = fields.Many2one('approval.request',string="Approval Request")

    is_hazardous = fields.Boolean(string='Hazardous',compute="_compute_hazardous_product",store=True)

    # EOI-439: Add budget_id for approver logic
    
    @api.depends('order_line','order_line.product_id','order_line.product_id.is_hazardous')
    def _compute_hazardous_product(self):
        for rec in self:
            rec.is_hazardous = False
            hazard = rec.order_line.filtered(lambda line: line.is_hazardous == True)
            if len(hazard) >= 1:
                rec.is_hazardous = True
    
    @api.depends('state')
    def compute_state(self):

        for line in self:
            line.cfs_approval_state = line.state
    
    # EOI-341: Function to open a view (instead of using a window_action)
    def open_po_lines(self):
        context = {
            'search_default_order_id':self.id,
            'default_date_planned':self.date_planned
        }
        return {
            'res_model': 'purchase.order.line',
            'type':'ir.actions.act_window',
            'name':'Purchase Order Lines',
            'view_mode':'tree',
            'domain':[['order_id.id','=',self.id]],
            'view_id': self.env.ref('purchase_request.expanded_po_lines').id,
            'context': context
        }
    
    # EOI-345: Server Action Recreate Burdens
    def recreate_burdens(self):
        for rec in self:
            if rec.state in ['approved']:
                rec.order_line.recreate_burdens('b')
            elif rec.state in ['purchase']:
                rec.order_line.recreate_burdens('c')
                rec.order_line.retrieve_qty_received_burden()
                rec.order_line.retrieve_qty_billed_burden()

class PurchaseRequestLines(models.Model):
    _inherit = 'purchase.order.line'

    # EOI-341: Adding fields for expanded tree view and list view
    buyer_id = fields.Many2one(related='order_id.cfs_buyer', string='Buyer',)
    # quality_codes = fields.Many2many(comodel_name='product.quality.code', string='Quality Codes')
    requester_id = fields.Many2one('res.users','Requester', related='order_id.requester_id')
    free_description = fields.Char(string='Description')
    buyer_category_id = fields.Many2one('product.tag', string='Category')
    billed_percent = fields.Float(string='% Billed', digits=(3,2), compute='_compute_billed_percent', store=True)
    release_date = fields.Date(string='PO Release Date', compute='_compute_release_date', store=True)

    # EOI-345 Migrate fields from UAT v14;
    #   fields from cfs_stock_config 
    cfs_line_number = fields.Integer(related='sequence', string='Line')
    cfs_equipment = fields.Many2one(comodel_name='maintenance.equipment',string='Equipment')
    #   fields from cfs_purchase_sprint
    cfs_tracking = fields.Selection(related='product_id.tracking',string='Serialization')
    #   fields from cfa_approval
    cfs_request_origin = fields.Many2one('approval.request',string="PR")

    # EOI-347: Added Product UoM
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure")

    is_hazardous = fields.Boolean(string='Hazardous',related="product_id.is_hazardous")
    
    cfs_product_name = fields.Char(string="Product Name", related="product_id.name", readonly=True)
    cfs_vendor_part = fields.Char(string="Vendor Part", required=False, )
    cfs_quality_codes = fields.Many2many("product.quality.code", string="Quality Codes", )

    product_id = fields.Many2one("product.product", string="CFS Part",)
    override_account_id = fields.Many2one("account.account", string="GL Account", store=True)

    # EOI-347: Need field in PO Line List View
    po_deliver_to = fields.Many2one(string="Deliver To", related="order_id.picking_type_id")
    is_prod = fields.Boolean(string="is production", compute="_compute_production")

    # EOI-372 Warehouse onchange actions
    @api.depends('order_id.picking_type_id', 'order_id.picking_type_id.warehouse_id')
    def _compute_production(self):
        for rec in self:
            prod = False
            if rec.order_id.picking_type_id.warehouse_id and rec.order_id.picking_type_id.warehouse_id.wh_type == 'production':
                prod = True
            rec.is_prod = prod

    def _update_quality_code(self):
        for rec in self:
            if rec.product_id and rec.product_id.quality_codes:
                rec.write({'cfs_quality_codes': [(6,0,rec.product_id.quality_codes.ids)]})

    # EOI-438: Draft Purchase Order / Purchase Order: GL Account field
    @api.onchange("product_id", "buyer_category_id")
    def _onchange_product_or_category(self):
        for pol in self:
            override_account_id = False
            if not isinstance(pol.order_id, models.NewId) and pol.product_id and pol.product_id.quality_codes:
                pol._update_quality_code()
            if pol.product_id.property_account_expense_id:
                override_account_id = pol.product_id.property_account_expense_id.id
            elif pol.product_id.categ_id.property_account_expense_categ_id:
                override_account_id = pol.product_id.categ_id.property_account_expense_categ_id.id
            if pol.buyer_category_id and pol.buyer_category_id.default_purchase_account:
                override_account_id = pol.buyer_category_id.default_purchase_account.id
            pol.override_account_id = override_account_id

    # EOI-341: Added to calculate release_date
    @api.depends('date_planned', 'product_id.product_tmpl_id.seller_ids', 'order_id.partner_id')
    def _compute_release_date(self):
        def create_is_relevant_supplierinfo(vendor, quantity, order_date):
            def is_relevant_supplierinfo(info):
                relevant = vendor == info.name and info.min_qty <= quantity
                if order_date and info.date_start:
                    relevant &= info.date_start <= order_date
                if order_date and info.date_end:
                    relevant &= order_date <= info.date_end
                return relevant
            return is_relevant_supplierinfo

        for line in self:
            order_date = line.order_id.effective_date.date() if line.order_id.effective_date else False
            vendor = line.order_id.partner_id
            info = line.product_id.product_tmpl_id.seller_ids.filtered(create_is_relevant_supplierinfo(vendor, line.product_uom_qty, order_date))
            if len(info) > 1:
                info = max(info, key=lambda rec: rec.min_qty)
            release_date = line.date_planned
            if release_date and info.delay:
                release_date -= timedelta(days=info.delay)
            line.release_date = release_date or fields.Date.today()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for pol in self:
            if pol.product_id.product_tmpl_id.property_account_expense_id.id:
                pol.override_account_id = pol.product_id.product_tmpl_id.property_account_expense_id.id
            elif pol.product_id.categ_id.property_account_expense_categ_id.id:
                pol.override_account_id = pol.product_id.categ_id.property_account_expense_categ_id.id

    @api.depends('qty_invoiced')
    def _compute_billed_percent(self):
        for line in self:
            if line.qty_invoiced > 0 and line.price_subtotal > 0:
                line.billed_percent = line.qty_invoiced * line.price_unit / line.price_subtotal * 100
            else:
                line.billed_percent = 0.0