# -*- coding: utf-8 -*-

from odoo import models


class CFSBankAccountChatter(models.Model):
    _name = 'res.partner.bank'
    _inherit = ['res.partner.bank','mail.thread','mail.activity.mixin']

