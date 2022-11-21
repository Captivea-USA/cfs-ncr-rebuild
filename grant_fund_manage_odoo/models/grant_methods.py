# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GrantMethods(models.Model):
    _name = "grant.methods"
    _description = 'Grant Methods'

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string="Code",
        required=True,
    )