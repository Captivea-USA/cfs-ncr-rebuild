# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GrantStages(models.Model):
    _name = "grant.stages"
    _description = 'Grant Stages'
    _rec_name = 'custom_name'

    custom_name = fields.Char(
        string="Stage Name",
        required = True
    )
    custom_sequence = fields.Integer(
        string="Sequence",
        required = True,
        default=1
    )
    fold = fields.Boolean(
        string="Folded in Kanban"
    )
    custom_is_submited = fields.Boolean(
        string='Is Submitted'
    )