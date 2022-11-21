# -*- coding: utf-8 -*-

from odoo import models
#from odoo import models, api odoo13


class CostSheet(models.Model):
    _inherit = 'job.costing'

#    @api.multi odoo13
    def show_budget_line_custom(self):
        self.ensure_one()
#        res = self.env.ref('job_costing_budget_contracting_enterprice.action_budget_line_report') odoo13
        res = self.env.ref('job_costing_budget_contracting_enterprice.action_budget_line_report_custom')
        res = res.sudo().read()[0]
        res['domain'] = str([('costsheet_id', '=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
