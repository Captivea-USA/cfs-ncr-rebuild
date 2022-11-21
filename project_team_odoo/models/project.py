# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'
    
    @api.onchange('project_team_id')
    def onchange_project_team(self):
        for rec in self:
            rec.user_id = rec.project_team_id.project_manager_id.id
            rec.team_member_ids = [(6,0,rec.project_team_id.team_member_ids.ids)]
        
    
    project_team_id = fields.Many2one(
        'project.project.team',
        string='Project Team',
        copy=False
    )
    team_member_ids = fields.Many2many(
        'res.users',
        'team_project_team_res_user',
        string='Team Members',
        copy=False
    )

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    #odoo 13 
    #@api.onchange('project_id')
    # def _onchange_project(self):
    #     for rec in self:
    #         if rec.project_id:
    #             rec.project_team_id = rec.project_id.project_team_id.id
                
    #     return super(ProjectTask, self)._onchange_project()

    @api.onchange('project_id')
    def _onchange_project_custom(self):
        for rec in self:
            if rec.project_id:
                rec.project_team_id = rec.project_id.project_team_id.id
    
    project_team_id = fields.Many2one(
        'project.project.team',
        string='Project Team',
        copy=False
    )
    