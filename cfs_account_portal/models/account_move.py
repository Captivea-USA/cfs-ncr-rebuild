# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    acc_type = fields.Selection(string="Account Type", related="partner_bank_id.acc_type")