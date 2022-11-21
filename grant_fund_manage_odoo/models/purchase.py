# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    custom_received_grant_application_id = fields.Many2one(
        'crm.lead',
        domain = [('custom_is_grant_maker', '=', True)],
        string="Received Grant Application"
    )
