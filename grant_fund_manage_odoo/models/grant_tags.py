# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GrantTags(models.Model):
    _name = "grant.tags"
    _description = 'Grant Tags'

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string="Code",
        required=True
    )
    color = fields.Integer(
        'Color Index'
    )