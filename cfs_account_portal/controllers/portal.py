# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
#from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression

class CustomerPortal(CustomerPortal):

    MANDATORY_BANK_ACCOUNT_FIELDS = ["acc_number", "account_type", "acc_holder_name", "b_name", "currency_id"]
    OPTIONAL_BANK_ACCOUNT_FIELDS = ["aba_routing", "swift"]

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="user", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        return super(CustomerPortal, self).portal_my_invoice_detail(
            invoice_id,
            access_token=access_token,
            report_type=report_type,
            download=download,
            **kw
        )

    @http.route(['/my/bank_accounts', '/my/bank_accounts/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_bank_accounts(self, page=1, date_begin=None, date_end=None, sortby=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ResPartnerBank = request.env['res.partner.bank']

        domain = ['|',
            ('partner_id', '=', partner.id),
            ('partner_id', '=', partner.parent_id and partner.parent_id.id or partner.id)
        ]

        searchbar_sortings = {
            'name': {'label': _('Bank'), 'order': 'b_name desc'},
            'ban': {'label': _('Account Number'), 'order': 'acc_number'},
            'type': {'label': _('Type of Account'), 'order': 'account_type'},
            'aba': {'label': _('ABA/Routing'), 'order': 'aba_routing'},
            'currency': {'label': _('Currency'), 'order': 'currency_id desc'},
            'holder_name': {'label': _('Account Holder Name'), 'order': 'acc_holder_name'},
        }
        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        bank_count = ResPartnerBank.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/bank_accounts",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=bank_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        banks = ResPartnerBank.sudo().search_read(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_banks_history'] = [bank['id'] for bank in banks][:100]

        # Convert account_type value from selection code to text tag (e.g. 'c' -> 'Checking')
        account_types = dict(request.env['res.partner.bank'].fields_get(allfields=['account_type'], attributes=['selection'])['account_type']['selection'])
        for bank in banks:
            bank['account_type'] = account_types.get(bank['account_type'])

        values.update({
            'date': date_begin,
            'banks': banks,
            'page_name': 'bank',
            'pager': pager,
            'default_url': '/my/bank_accounts',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("cfs_account_portal.portal_my_bank_accs", values)

    @http.route(['/my/bank_accounts/<int:bank_id>'], type='http', auth="user", website=True)
    def portal_my_bank_acc(self, bank_id, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        partner_to_search = partner.parent_id and partner.parent_id.id or partner.id
        bank_acc = request.env['res.partner.bank'].sudo().search([('partner_id', '=', partner_to_search), ('id', '=', bank_id)])

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.bank_account_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BANK_ACCOUNT_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BANK_ACCOUNT_FIELDS if key in post})
                bank_acc.sudo().write(values)
                return request.redirect('/my/bank_accounts')

        currency = request.env['res.currency'].sudo().search([])
        account_types = bank_acc.fields_get(allfields=['account_type'], attributes=['selection'])['account_type']['selection']
        
        values.update({
            'bank_acc': bank_acc,
            'account_types': account_types,
            'currencies': currency,
            'redirect': redirect,
            'page_name': 'my_bank',
        })
        values.update(bank_acc._get_decrypted_vals())

        response = request.render("cfs_account_portal.portal_my_bank_acc", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/my/bank_accounts/new'], type='http', auth="user", website=True)
    def portal_new_bank_acc(self, redirect=None, **post):
        partner = request.env.user.partner_id
        values = {}

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.bank_account_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BANK_ACCOUNT_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BANK_ACCOUNT_FIELDS if key in post})
                values['partner_id'] = partner.parent_id and partner.parent_id.id or partner.id
                bank_acc = request.env['res.partner.bank'].sudo().create(values)
                return request.redirect('/my/bank_accounts')

        currency = request.env['res.currency'].sudo().search([])
        account_types = request.env['res.partner.bank'].fields_get(allfields=['account_type'], attributes=['selection'])['account_type']['selection']

        values.update({
            'account_types': account_types,
            'currencies': currency,
            'redirect': redirect,
            'page_name': 'my_bank',
        })

        response = request.render("cfs_account_portal.portal_my_new_bank_acc", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def bank_account_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_BANK_ACCOUNT_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.MANDATORY_BANK_ACCOUNT_FIELDS + self.OPTIONAL_BANK_ACCOUNT_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message
