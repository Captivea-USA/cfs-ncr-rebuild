# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Contacts(models.Model):
    _inherit='res.partner'

    # EOI-340: Overriding type and adding more selections
    type = fields.Selection(
        [('accounting', 'Accounting'),
         ('contact', 'Contact'),
         ('delivery', 'Delivery/Shipping'),
         ('invoice', 'Invoice/Billing'),
         ('other', 'Other'),
         ("private", "Private"),
         ('quality', 'Quality'),
         ('returns', 'Returns'),
         ('sales', 'Sales'),
         ('sourcing', 'Sourcing'),
        ], string='Address Type',
        default='contact',
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")
        
    # EOI-245: add custom fields, and the funtions for calculation
    @api.model
    def _buyer_domain(self):
        # EOI-322: Auto populate Buyer on Purchase Orders
        # This returns an empty list because we do not have
        # permissions in the system yet
        return []
        
        # if self.env.ref('cfs_budget_burden.cfs_buyer_group',raise_if_not_found=False):
        #     domain = self.env.ref('cfs_budget_burden.cfs_buyer_group').users.ids
        # else:
        #     domain = False
        # return [('id', 'in', domain)]

    @api.depends('purchase_order_count')
    def _compute_last_po_date(self):
        for partner in self:
            last_po = self.env['purchase.order'].search([('partner_id', '=', partner.id)], order='effective_date desc',
                                                        limit=1)
            partner.last_po_date = last_po.effective_date

    @api.depends('purchase_order_count')
    def _compute_last_invoice_date(self):
        for partner in self:
            last_invoice = self.env['account.move'].search([('partner_id', '=', partner.id)], order='date desc',
                                                           limit=1)
            partner.last_invoice_date = last_invoice.date

    # Fields from UAT v14

    ref = fields.Char('Ref / Contact ID')
    website = fields.Char('Website Link')
    #EOI 354 changed comodel relation
    cfs_shipping_method = fields.Many2one('res.partner.shipping.method', string='Vendor Shipping')

    doing_business_as = fields.Char(string='Doing Business As')
    is_grantor = fields.Boolean(string='Grantor')
    property_delivery_carrier_id = fields.Many2one('delivery.carrier', 
                                                    string='Delivery Method')
    incoterms = fields.Many2one('account.incoterms', 
                                string='Incoterms')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('consider', 'Under Consideration'),
        ('ok','Approved'),
        ('bad','Disqualified'),
        ('inactive','Inactive'),
        ('restrict','Restricted')
        ], 
        string='Status')
    buyer_id = fields.Many2one('res.users', 
                                string='Buyer',
                                domain=_buyer_domain ,
                                help='The internal Purchase user in charge of this contact.')
    last_po_date = fields.Date('Last PO Date', 
                                compute=_compute_last_po_date)
    last_invoice_date = fields.Date('Last Invoice Date', 
                                    compute='_compute_last_invoice_date')
    is_bills = fields.Boolean('Can Bill w/o PO')
    tax_id_type = fields.Selection([
        ('emp', 'Employer ID'),
        ('ss', 'SS'),
        ('non_usa', 'Foreign')
        ], 
        string='Tax ID Type')
    business_structure = fields.Selection([
        ('corp', 'Corporation'),
        ('llc','LLC'),
        ('llp','LLP'),
        ('sole','Sole Proprietorship'),
        ('scorp','S Corporation')
        ], 
        string='Business Structure')
    ten99_reporting = fields.Boolean('1099 Reporting')
    commodity_code_ids = fields.Many2many('commodity.code', 
                                        string='Scope of Approval')
    db_number = fields.Char(string='D&B Number')
    db_score = fields.Char(string='D&B Score')
    date_of_db_score = fields.Date(string='Date of D&B Score')
    last_review_date = fields.Date(string='Last Review Date')
    review_results = fields.Char(string='Last Review Rating')
    next_review_date = fields.Date(string='Next Review Due')
    last_audit_date = fields.Date(string='Last Audit Date')
    audit_results = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('correct','Pass with Corrective Actions')
        ], 
        string='Last Audit Results')
    next_audit_date = fields.Date('Next Audit Date')


    @api.onchange('status')
    def _onchange_status(self):
        for rec in self:
            if rec.status in ['bad','inactive']:
                rec.active = False
            if not rec.active and rec.status not in ['bad','inactive']:
                rec.active = True
