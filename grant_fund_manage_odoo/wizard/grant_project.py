# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CustomGrantProjectWizard(models.TransientModel):
    _name = 'custom.grant.project.wizard'
    _description = 'Custom Grant Project Wizard'

    @api.model
    def default_get(self, fields):
        res = super(CustomGrantProjectWizard, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'grant.seeker.application':
            record = self.env[model].browse(active_id)
            res.update({
                'name': record.custom_name,
                'project_manager_id': record.custom_manager_id.id,
                'custom_description': record.custom_description,
                'custom_grant_seeker_id': record.id
            })
        return res

    name = fields.Char(
        string="Name",
        required = True
    )
    project_manager_id = fields.Many2one(
        'res.users',
        string="Project Manager",
        required = True
    )
    custom_description = fields.Text(
        string="Description",
        required = True
    )
    custom_grant_seeker_id = fields.Many2one(
        'grant.seeker.application',
        string="Grant Seeker Application"
    )

    def custom_create_grant_project(self):
        vals = {
            'name': self.name,
            'user_id': self.project_manager_id.id,
            'custom_description': self.custom_description,
            'custom_grant_seeker_id': self.custom_grant_seeker_id.id,
            'custom_is_grant_seeker': True
        }
        project_id = self.env['project.project'].sudo().create(vals)
        if project_id:
            self.custom_grant_seeker_id.custom_project_id = project_id.id
        res_act = self.env.ref('project.open_view_project_all')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('id', 'in', project_id.ids)])
        return res_act