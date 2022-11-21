# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class AccountMove(models.Model):
    _inherit = "account.move"

    custom_grant_application_id = fields.Many2one(
        'grant.seeker.application',
        string="Grant Seeker Application"
    )
    custom_grant_lead_id = fields.Many2one(
        'crm.lead',
        string="Grant Request / Application"
    )