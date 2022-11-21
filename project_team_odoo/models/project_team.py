# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTeamCustom(models.Model):
    _name = 'project.project.team'
    
    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
    )
    code = fields.Char(
        string='Code',
        required=True,
        copy=False,
    )
    project_manager_id = fields.Many2one(
        'res.users',
        string='Project Manager',
        required=True,
        copy=False,
    )
    team_member_ids = fields.Many2many(
        'res.users',
        'project_team_res_user',
        string='Team Members',
        copy=False,
    )
    notes = fields.Text(
        string='Internal Notes',
        copy=False
    )
    