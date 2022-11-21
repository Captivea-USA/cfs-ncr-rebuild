# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    remittance_advice = fields.Boolean('Remittance Advice')
    show_remittance_advice = fields.Boolean('show Remittance Advice Report')

    @api.onchange('remittance_advice')
    def _onchange_remittance_advice(self):
        if self.remittance_advice:
            self.template_id = self.env.ref('remittance_advice_report_omax.mail_template_data_payment_receipt_remittance_advice').id
        else:
            if self.show_remittance_advice:
                self.template_id = self.env.ref('account.mail_template_data_payment_receipt').id

    @api.model
    def default_get(self, fields):
        rec = super(MailComposeMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if active_model == 'account.payment' and self.env.context.get('active_id'):
            payment_rec = self.env['account.payment'].browse(self.env.context.get('active_id'))
            if payment_rec:
                if payment_rec.payment_type == 'outbound':
                    rec.update({'show_remittance_advice':True})
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
