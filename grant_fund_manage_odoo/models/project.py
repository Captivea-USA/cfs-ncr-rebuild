# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class ProjectProject(models.Model):
    _inherit = "project.project"

    custom_grant_seeker_id = fields.Many2one(
        'grant.seeker.application',
        string="Grant Seeker Application"
    )
    custom_is_grant_seeker = fields.Boolean(
        string="Is Grant Seeker"
    )
    custom_description = fields.Text(
        string="Description"
    )

    def custom_show_grant_opportunity(self):
        for rec in self:
            res = self.env.ref('crm.crm_lead_action_pipeline')
            res = res.sudo().read()[0]
            res['domain'] = str([('custom_grant_seeker_id', 'in', rec.custom_grant_seeker_id.ids)])
        return res