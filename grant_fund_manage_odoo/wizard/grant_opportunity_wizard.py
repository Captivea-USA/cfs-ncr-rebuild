# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CustomGrantOpportunityWizard(models.TransientModel):
    _name = 'custom.grant.opportunity.wizard'
    _description = 'Custom Grant Opportunity Wizard'

    partners_ids = fields.Many2many(
        'res.partner',
        string="Grant Makers"
    )

    def create_opportunity_vals(self, active_id, partner):
        vals = {
            'name': active_id.custom_name,
            'partner_id': partner.id,
            'custom_grant_seeker_id': active_id.id,
            'custom_proposal': active_id.custom_proposal,
            'custom_is_grant_seeker': True,
            'type': 'opportunity'
        }
        return vals

    def create_custom_grant_opportunity(self):
        active_model = self.env.context['active_model']
        active_id = self.env.context['active_id']
        crm_lead_ids = []
        if active_model == 'grant.seeker.application':
            active_id = self.env[active_model].browse(int(active_id))
            for partner in self.partners_ids:
                vals = self.create_opportunity_vals(active_id,partner)
                crm_lead_id = self.env['crm.lead'].sudo().create(vals)
                crm_lead_ids.append(crm_lead_id.id)
        res_act = self.env.ref('grant_fund_manage_odoo.custom_grant_lead_action_pipeline')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('id', 'in', crm_lead_ids)])
        return res_act