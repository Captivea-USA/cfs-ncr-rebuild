# -*- coding: utf-8 -*-
from odoo import models, fields, _


class UserApprovalTags(models.Model):
    _name = "user.approval.tags"
    _description = "User Approval Tags"

    user_id = fields.Many2one('res.users')
    name = fields.Char('Name', related='user_id.name')
    color = fields.Integer(string='Color', default=0)
    request_level_id = fields.Many2one('multi.approval.line')
