
from odoo import api,fields, models, _
from odoo.exceptions import UserError
from datetime import datetime

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    # EOI-341: Needed for relation from approval.product.line
    purchase_order = fields.Many2one('purchase.order',string="Previous PO")

    name = fields.Char(string='Purchase Request', tracking=True)
    cap_type = fields.Selection([('new', 'New'), ('change_order', 'Change Order')], string="Type", required=True, default='new')
    cap_ship_to = fields.Selection([('cfs', 'CFS'), ('external', 'External'), ('request_new_address', 'Request New Address')], string="Ship To", required=True, default='cfs',
    help="Products: This is the address where the products will be signed for, received into inventory.\n\n" +\
                   "Services: This is the address where the service will be signed for or performed.\n\n" + \
                   "PROD Warehouses: For use in SPARC, subject to Vendor Quality and Inspection requirements.\n" + \
                   "R&D Warehouses: Not for use in SPARC, relaxed Quality and Inspection requirements.\n" +\
                   "Asset Warehouses: For the storage of long lead time spare parts used to repair CFS Assets.\n\n\n" + \
                   "Note: If the request isn't for Products or Services that will be signed for or received, choose the Main Warehouse" +
                   "      closest to your location.")
    hide_address = fields.Boolean(string='Hide Address',compute="_compute_hide_address")

    cap_warehouse = fields.Many2one('stock.warehouse', string="Warehouse")
    cap_remote_warehouse = fields.Many2one('stock.warehouse', string="Remote Warehouse")
    cap_address = fields.Char(string="Address")
    cap_need_date = fields.Date(string="Need Date")
    cap_request_notes = fields.Text(string="Requestor Notes")
    cap_project_id = fields.Many2one('project.project', string='Project')
    cap_notes = fields.Text(string=" RequesterNotes")

    cap_self_approved = fields.Boolean(string="Self Approved")
    cap_self_approved_timestamp = fields.Datetime(string="Self Approved Timestamp")

    cap_buyer_ids = fields.Many2many('res.users', string="Buyers")
    cap_vendor_ids = fields.Many2one('res.partner', string="Vendors")

    # EOI-464: Budget and requester fields needed to pass into Draft PO
    analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    requester_id = fields.Many2one('res.users', string="Requester", related='request_owner_id')

    @api.onchange('cap_ship_to', 'cap_remote_warehouse')
    def _compute_hide_address(self):
        """EOI513 - when ship to is changed, compute value of hide address
        hide_address is used on the xml to compute what is required/invisible
        """
        my_house = self.env.ref('cap_purchase_form_view.my_house')
        
        for record in self:
            cap_ship_to = record.cap_ship_to
            record.hide_address = True
            if cap_ship_to == 'request_new_address':
                record.hide_address = False
                record.cap_remote_warehouse = False
                record.cap_warehouse = False
            if cap_ship_to == 'external':
                record.cap_warehouse = False
        #   only display address on remote warehouse if my_house is used
            if cap_ship_to == 'external' and my_house and record.cap_remote_warehouse and record.cap_remote_warehouse.id == my_house.id:
                record.hide_address = False

    @api.model
    def create(self, vals):
        """EOI530 - require vendor part or description for use in chatter
        check for any errors when creating
        """
        if vals.get('product_line_ids'):
            error = ""
            for line in vals.get('product_line_ids'):
                # find the dict index that is the dict
                product_line = {}
                for l in line:
                    if type(l) is dict:
                        product_line = l
                product = self.env["product.product"].browse(product_line.get('product_id'))
                if product and not product_line.get('cap_vendor_part') and not product_line.get('description'):
                    # test the procurement type of the product
                    if product.categ_id.procurement_type != 'direct':
                        error += f"Indirect Product {product.name} must have a Vendor Part or a Description.\n"
                    else:
                        error += f"Direct Product {product.name} must have a Vendor Part.\n"
                # if there is a product category for a direct product, remove it
                if product and product.categ_id.procurement_type == 'direct' and product_line.get('buyer_category_id'):
                    error += f"A Buyer Category is not relevant for Direct Product {product.name}.\n"
            if error:
                raise UserError(f'{error}\n\nPlease correct the above items and try again.')
        return super().create(vals)

    def write(self,vals):
        """EOI530 - require vendor part or description for use in chatter
        """
        if vals.get('product_line_ids'):
            error = []
            for product_line in vals.get('product_line_ids'):
                # find the dict index that is the dict
                # EOI599: only test if dict
                if type(product_line) is dict:
                    product = self.env["product.product"].browse(product_line.get('product_id'))
                    if product and not product_line.get('cap_vendor_part') and not product_line.get('description'):
                        # test the procurement type of the product
                        if product.categ_id.procurement_type != 'direct':
                            error += f"Indirect Product {product.name} must have a Vendor Part or a Description.\n"
                        else:
                            error += f"Direct Product {product.name} must have a Vendor Part.\n"
                    # if there is a product category for a direct product, remove it
                    if product and product.categ_id.procurement_type == 'direct' and product_line.get('buyer_category_id'):
                        error += f"A Buyer Category is not relevant for Direct Product {product.name}.\n"
            if error:
                raise UserError(f'{error}\n\nPlease correct the above items and try again.')
        return super().write(vals)

    @api.onchange('cap_self_approved')
    def self_approved_timestamp(self):
        if self.cap_self_approved:
            self.cap_self_approved_timestamp = fields.Datetime.now()

    # EOI-341: Function to open a view (instead of using a window_action)
    def open_ap_lines(self):
        context = {
            'default_approval_request_id':self.id,
        }
        return {
            'res_model': 'approval.product.line',
            'type':'ir.actions.act_window',
            'name':'Purchase Request Lines',
            'view_mode':'tree',
            'domain':[['approval_request_id.id','=',self.id]],
            'view_id': self.env.ref('cap_purchase_form_view.approval_product_line_view_tree_expanded_inherit').id,
            'context': context,
        }

    # EOI-433: validate every line in Request has vendor
    def check_line_vendors(self):
        lines_without_vendor = self.product_line_ids.filtered(lambda line: not line.cap_vendor_name)
        if lines_without_vendor :
            msg  = 'Vendor is missing from ' 
            msg += self.name
            raise UserError(msg)

    # EOI-433: Override base function to create PO's after approved
    # TODO this should be refactored for performance in the future, I don't think we need this many loops
    # todo I've found several instances of commented lines of code that don't serve a purpose (not noted as to why they're commented)
    def action_create_purchase_orders(self):
        """ Create and/or modifier Purchase Orders. """
        self.check_line_vendors()
        self.ensure_one()

        vendor_ids = self.product_line_ids.mapped('cap_vendor_name')
        new_purchase_order = False

        # EOI-469: Creating Draft POs grouped by Vendors, by looping by vendors instead of lines
        for vendor in vendor_ids:
            lines_with_vendors = self.product_line_ids.filtered(lambda line: line.cap_vendor_name.id == vendor.id)
            po_line_vals = []
            po_vals = {
                    'partner_id':vendor.id,
                    'analytic_id':self.analytic_id.id,
                    'cfs_buyer':self.env.user.id,
                    'approval_request_id': self.id,
                    }
            # EOI-464: Passes the budget_id and requester_id into PO
            po_vals['requester_id'] = self.requester_id.id


            new_purchase_order = self.env['purchase.order'].create(po_vals)
            # EOI- 526 PR Fields transfers on PO via onchange
            new_purchase_order.onchange_partner_id()

            for line in lines_with_vendors:
                # EOI-464: Passes the account_id dependent on what is available
                if line.product_id.product_tmpl_id.property_account_expense_id.id:
                    account = line.product_id.product_tmpl_id.property_account_expense_id.id
                elif line.product_id.product_tmpl_id.categ_id.property_account_expense_categ_id.id:
                    account = line.product_id.product_tmpl_id.categ_id.property_account_expense_categ_id.id
                elif line.cap_vendor_name.property_account_payable_id.id:
                    account = line.cap_vendor_name.property_account_payable_id.id

                # EOI-469: Build and Add dictionaries for every line with the same vendor
                # EOI-507: Modified the po_line_vals assignment and data structure to just be '=' and be a dictionary '{}'
                po_line_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'product_uom': line.product_uom_id.id,
                    'company_id': self.company_id.id,
                    'date_promised': datetime.today(),
                    'price_unit': line.cap_price,
                    'override_account_id': account,
                    'name':line.cap_vendor_name.name,
                    'order_id': new_purchase_order.id,
                    # EOI-372: Add Quality Codes on PO creation
                    'cfs_quality_codes':line.quality_codes,
                    'free_description': line.description ,
                    'cfs_vendor_part': line.cap_vendor_part,
                    }

                new_po_line = self.env['purchase.order.line'].create(po_line_vals)

                # EOI-469: Re-factored for PO creation by vendor (For Smart Button)
                for po_line in new_po_line:
                    line.purchase_order_line_id = po_line.id
                    new_purchase_order.order_line = [(4, po_line.id)]
                
                # EOI-472: Create Chatter for each new created PO
                po_desc = pr_desc = ''
                if line.product_id.name:
                    pr_desc += f'{line.product_id.name}'
                if line.cap_vendor_part:
                    po_desc += f'[{line.cap_vendor_part}]'
                    pr_desc += f'({line.cap_vendor_part})'
                if line.description:
                    po_desc += f'{line.description}'
                if line.approval_request_id:
                    approval_request = line.approval_request_id
                # set default values if the strings and null
                po_desc = 'Unknown Product' if not po_desc else po_desc
                pr_desc = 'Unknown Product' if not pr_desc else pr_desc
                new_purchase_order.message_post(
                    body=f'{po_desc} from request <a href="#" data-oe-model="approval.request" data-oe-id="{approval_request.id}">{approval_request.name}</a> added'
                )
                # if reason
                if self.reason:
                    new_purchase_order.message_post(
                        body=f'Reason for Request: {self.reason}'
                    )
                # if notes
                # todo notes aren't carried over correctly
                if self.cap_request_notes:
                    new_purchase_order.message_post(
                        body=f'Requester Notes: {self.cap_request_notes}'
                    )
                # Chatter on the approval request
                line.approval_request_id.message_post(
                    body=f'{pr_desc} converted into <a href="#" data-oe-model="purchase.order" data-oe-id="{new_purchase_order.id}">{new_purchase_order.name}</a>!'
                )
        # todo we should return something so that we can unit test in the future
        # EOI- 529 Draft PO Create from a PR
        if new_purchase_order:
            return {
                    'name': _('Purchase Orders'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    "res_id": new_purchase_order.id,
                }
        return True

