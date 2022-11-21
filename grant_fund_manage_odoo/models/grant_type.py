# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GrantTypes(models.Model):
    _name = "grant.types"
    _description = 'Grant Types'

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string="Code",
        required=True
    )