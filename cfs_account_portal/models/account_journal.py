# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.base.models.res_bank import sanitize_account_number


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = 'account.journal'

    def set_bank_account(self, acc_number, bank_id=None):
        """ Create a res.partner.bank (if not exists) and set it as value of the field bank_account_id """
        self.ensure_one()
        res_partner_bank = self.env['res.partner.bank'].search(
            [('sanitized_acc_number', '=', self.env['res.partner.bank']._decrypt_data(sanitize_account_number(acc_number))),
             ('company_id', '=', self.company_id.id)], limit=1)

        if res_partner_bank:
            self.bank_account_id = res_partner_bank.id
        else:
            self.bank_account_id = self.env['res.partner.bank'].create({
                'acc_number': acc_number,
                'bank_id': bank_id,
                'company_id': self.company_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.company_id.partner_id.id,
            }).id