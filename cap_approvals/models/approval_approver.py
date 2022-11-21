from odoo import models, fields, api, _

class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    user_ids = fields.Many2many('res.users',string="To Approve")