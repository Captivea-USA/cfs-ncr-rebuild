# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    grant_application_ids = fields.Many2many(
        'grant.seeker.application',
        'grant_seeker_application_budget',
        string="Grant Applications"
    )
    grant_types_ids = fields.Many2many(
        'grant.types',
        string="Grant Types"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: