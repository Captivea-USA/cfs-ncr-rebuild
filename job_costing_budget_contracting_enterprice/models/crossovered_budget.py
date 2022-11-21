# -*- coding: utf-8 -*-

#from odoo import models, api odoo13
from odoo import models

class CrossOveredBudget(models.Model):
#     _inherit = 'account.analytic.crossovered.budget'
    _inherit = 'crossovered.budget'
    
#    @api.multi odoo13
    def show_costsheet_custom(self):
        self.ensure_one()
        costsheet_ids = []
        for rec in self:
            for line in rec.crossovered_budget_line:
                costsheet_ids.append(line.costsheet_id.id)
        res = self.env.ref('odoo_job_costing_management.action_job_costing')
        res = res.sudo().read()[0]
        res['domain'] = str([('id', 'in', costsheet_ids)])
        return res

#    @api.multi odoo13
    def show_costsheet_line_custom(self):
        self.ensure_one()
        sheetline_ids = []
        for rec in self:
            for line in rec.crossovered_budget_line:
                sheetline_ids.append(line.jobcost_line_id.id)
        res = self.env.ref('job_costing_budget_contracting_enterprice.action_cost_sheet_line')
        res = res.sudo().read()[0]
        res['domain'] = str([('id', 'in', sheetline_ids)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
