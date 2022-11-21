# todo this file should be renamed to match the naming scheme of the other py file in this module
from odoo import api,fields, models
from odoo.exceptions import UserError

class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    def _warehouse_default(self):
        """EOI513 - Set default warehouse list
        """
        cap_ship_to = self.env.context.get('cap_ship_to')
        cap_warehouse = self.env.context.get('cap_warehouse')
        cap_remote_warehouse = self.env.context.get('cap_remote_warehouse')
        if cap_ship_to == 'cfs':
            return cap_warehouse
        elif cap_ship_to == 'external':
            return cap_remote_warehouse
        else:
            return self.env['stock.warehouse'].search([('name','=','New')],limit=1)
    
    # Changed string from Products to CFS Part
    product_id = fields.Many2one('product.product', string="CFS Part", check_company=True)

    description = fields.Char(string="Description", required=False)

    # EOI-360 - needed in api.depends
    product_filter_ids = fields.Many2many('product.product', compute='_domain_products')
    wh_type = fields.Selection(related='cap_warehouse.wh_type')
    

    # EOI-341: Needed for approval.product.line expanded view
    date_promised = fields.Date(string='Promise Date')
    commodity_code = fields.Char(string="Commodity Code")
    prior_purchase_order = fields.Many2one("purchase.order", related="approval_request_id.purchase_order", string="Previous PO")
    current_purchase_order = fields.Many2one('purchase.order',string="PO", default=False)
    request_status = fields.Selection(string='Status',related='approval_request_id.request_status')
    cap_warehouse = fields.Many2one('stock.warehouse',related='approval_request_id.cap_warehouse',default=lambda self: self._warehouse_default())
    procurement_type = fields.Selection(related='product_id.categ_id.procurement_type')


    # EOI-332: Add fields to show up on the approval.request form view
    requester_id = fields.Many2one('res.users','Requester',related="approval_request_id.request_owner_id",store=True,compute='_compute_requester_id')
    buyer_id = fields.Many2one("res.users", string="Buyer")
    buyer_category_id = fields.Many2one('product.tag', string='Category')
    quality_codes = fields.Many2many(comodel_name='product.quality.code', string='Quality Codes')
    is_hazardous = fields.Boolean(string='Hazardous',related="product_id.is_hazardous")



    cap_product_name = fields.Char(string="Product Name", related="product_id.name")
    cap_need_date = fields.Date(string="Need Date", related='approval_request_id.cap_need_date')
    cap_vendor_name = fields.Many2one('res.partner',string="Vendor Name")
    cap_new_vendor_address = fields.Char(string="Address")
    cap_vendor_part = fields.Char(string="Vendor Part")
    cap_tracking = fields.Selection(related='product_id.tracking',string='Serialization')
    cap_price = fields.Float(string="Price", widget="monetary")
    cap_subtotal = fields.Float(string="Subtotal", widget="monetary", compute='_compute_subtotal')
    is_prod = fields.Boolean(string="is production", compute="_compute_production")

    # EOI-372 Warehouse onchange actions
    @api.depends('wh_type','approval_request_id.cap_warehouse.wh_type')
    def _compute_production(self):
        for rec in self:
            prod = False
            if rec.approval_request_id.cap_warehouse.wh_type and rec.approval_request_id.cap_warehouse.wh_type == 'production':
                prod = True
            rec.is_prod = prod
    
    @api.onchange('product_id','buyer_category_id','vendor_id')
    def _onchange_buyer_categ(self):
        for rec in self:
            if rec.product_id and rec.product_id.quality_codes:
                rec.quality_codes = rec.product_id.quality_codes.ids

    # EOI-437: Boolean to detect if a product is of the Indirect procurement type
    is_indirect = fields.Boolean(string="Is Indirect", default="False", compute="_is_product_indirect")

    # EOI-437: Checking if the product on approval.product.line is Indirect
    @api.onchange('product_id')
    def _is_product_indirect(self):
        check_indirect = self.filtered(lambda line: line.product_id.product_tmpl_id.categ_id.procurement_type == 'indirect')
        if check_indirect:
            self.is_indirect = True
            # raise UserError(str(self.is_indirect))
        elif not check_indirect:
            self.is_indirect = False
    
    # EOI-428: 6b) Made Requester populate with Requester from Purchase Request. If no PR, default Requester to current user
    @api.depends('approval_request_id.request_owner_id')
    def _compute_requester_id(self):
        if self.approval_request_id.request_owner_id:
            for rec in self:
                rec.requester_id = self.approval_request_id.request_owner_id

    # Calculates Subtotal * Quantity
    @api.depends('quantity', 'cap_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.cap_subtotal = rec.quantity * rec.cap_price

    # Changes name when CFS Part changes
    # @api.onchange('product_id')
    # def change_product_name(self):
    #     self.cap_product_name = self.product_id.name

    # EOI-433: Change vendor according to the vendor on product
    @api.onchange('product_id')
    def change_product_name(self):
        if self.product_id.seller_ids:
            self.cap_vendor_name = self.product_id.seller_ids[0].name.id

    # EOI-467: Finding a buyer for CFS Part
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

    @api.depends('wh_type')
    def _domain_products(self):
        """EOI460 - Raise warning if selecting product before warehouse
        """
        for rec in self:
            # If this is a new PR and ship to has been selected
            if not rec.cap_warehouse and rec.approval_request_id.cap_ship_to not in ('external','request_new_address'):
                raise UserError("Please select a Warehouse first.")
            # the product needs to be ok to be purchased
            products = self.env['product.product'].search([('purchase_ok','=', True),('can_be_expensed','!=',True)])
            rec.product_filter_ids = products.ids
