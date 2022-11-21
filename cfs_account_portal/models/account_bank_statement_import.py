# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _inherit = 'account.bank.statement.import'

    def _check_journal_bank_account(self, journal, account_number):
        # Needed for CH to accommodate for non-unique account numbers
        sanitized_acc_number = self.env['res.partner.bank']._decrypt_data(journal.bank_account_id.acc_number.split(" ")[0])
        return sanitized_acc_number == account_number
