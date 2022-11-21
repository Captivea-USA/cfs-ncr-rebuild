# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression


class AccountPayment(models.Model):
    _inherit = "account.payment"

class ResCompany(models.Model):
    _inherit = 'res.company'

    signature_image = fields.Image(string='Signature Image', max_width=128, max_height=128, store=True)

class MailTemplate(models.Model):
    _inherit = "mail.template"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('show_remittance_advice') and self._context.get('remittance_advice'):
            domain = []
        else:
            tmpl_id = self.env.ref('remittance_advice_report_omax.mail_template_data_payment_receipt_remittance_advice')
            domain = [('id', '!=', tmpl_id.id)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
