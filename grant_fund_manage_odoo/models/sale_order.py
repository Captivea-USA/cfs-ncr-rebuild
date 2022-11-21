# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if 'opportunity_id' in res:
            opportunity_id = self.env['crm.lead'].browse(res.get('opportunity_id'))
            res.update({
                'custom_grant_application_id': opportunity_id.custom_grant_seeker_id.id,
                'custom_grant_lead_id': opportunity_id.id,    
            })
        return res

    custom_grant_application_id = fields.Many2one(
        'grant.seeker.application',
        string="Grant Seeker Application"
    )
    custom_grant_lead_id = fields.Many2one(
        'crm.lead',
        string="Lead"
    )

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.custom_grant_application_id:
            res.update({
                'custom_grant_application_id': self.custom_grant_application_id.id,
                'custom_grant_lead_id': self.custom_grant_lead_id.id
            })
        return res