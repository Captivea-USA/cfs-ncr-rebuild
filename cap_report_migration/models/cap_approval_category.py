from odoo import models, fields, api, _


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    pr = fields.Boolean(string="Purchase Request", default=False)

