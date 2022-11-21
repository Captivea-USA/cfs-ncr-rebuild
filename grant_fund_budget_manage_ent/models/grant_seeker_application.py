# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class GrantSeekerApplication(models.Model):
    _inherit = 'grant.seeker.application'

    def action_view_grant_budgets(self):
        res_act = self.env.ref('account_budget.act_crossovered_budget_view')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('grant_application_ids', 'in', self.ids)])
        return res_act