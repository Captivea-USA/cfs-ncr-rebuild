# -*- coding: utf-8 -*-
from odoo import models, fields

# EOI-348: Added for many2many field 'description_ids'
class ToleranceDescription(models.Model):
    _name = 'account.tolerance.description'
    _description = 'Tolerance Description'

    name = fields.Char(string="Description")