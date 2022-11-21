# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError

APPROVED = 10
REFUSED = 6

class MultiApprovalLine(models.Model):
    _name = 'multi.approval.line'
    # EOI-532: Multi Approval description typos
    _description = 'Multi Approval Line'
    _order = 'sequence'

    name = fields.Char(string='Title', required=True)
    user_id = fields.Many2one(string='User', comodel_name="res.users",
                              required=True)
    sequence = fields.Integer(string='Sequence')
    require_opt = fields.Selection(
        [('Required', 'Required'),
         ('Optional', 'Optional'),
         ], string="Type of Approval", default='Required')
    approval_id = fields.Many2one(
        string="Approval", comodel_name="multi.approval")
    state = fields.Selection(
        [('Draft', 'Draft'),
         ('Waiting for Approval', 'Waiting for Approval'),
         ('Approved', 'Approved'),
         ('Refused', 'Refused'),
         ('Cancel', 'Cancel'),
         ], default="Draft")
    refused_reason = fields.Text('Refused Reason')
    deadline = fields.Date(string='Deadline')

    # EOI-349: Adding fields to match UAT v14
    user_approval_ids = fields.One2many('user.approval.tags', inverse_name='request_level_id', string='Done', readonly="True")
    level = fields.Integer(string="Level")
    min_approval = fields.Integer(string="Min. To Approve")
    everyone_approves = fields.Boolean(string="Everyone Approves")
    request_id = fields.Many2one('res.users',string="Requester")
    user_ids = fields.Many2many('res.users',string="To Approve")
    # to_approve = fields.Many2many('approval.approver')
    status = fields.Selection([
        ('new','New'),
        ('pending','To Approve'),
        ('approved','Approved'),
        ('refused','Refused'),
        ('cancel','Cancel')
    ], string="Status")
    action_timestamp = fields.Datetime(string="Action Timestamp", readonly=True)

    # 13.0.1.1
    def set_approved(self):
        self.ensure_one()
        self.state = 'Approved'

    def set_refused(self, reason=''):
        self.ensure_one()
        self.write({
            'state': 'Refused',
            'refused_reason': reason
        })

    # EOI-349: Changes tag color to green if APPROVED
    def is_level_approved(self):
        """Returns True if the number of approvals in the level is greater than or equal to the minimum approvals."""
        self.ensure_one()
        min_approvals = len(self.mapped('user_ids')) if self.everyone_approves else self.min_approval
        current_approvals = len(self.user_approval_ids.filtered(lambda a: a.color == APPROVED))
        # raise UserError(str(current_approvals))
        if current_approvals >= min_approvals:
            return True
        return False
    # EOI-349: Changes tag color to red if REFUSED
    def is_level_refused(self):
        """Returns True if at least one user in this level refused the request."""
        self.ensure_one()
        return True if self.user_approval_ids.filtered(lambda a: a.color == REFUSED) else False

    # EOI-349: Creates activities for users when it is time for them to approve
    def _create_activity(self):
        """EOI499 - Use an approval activity type
        """
        for approver in self:
            pending_users = approver.user_ids.filtered(lambda u: u not in approver.user_approval_ids.mapped('user_id'))
            for user in pending_users:
                if not approver.approval_id._get_user_approval_activities(user=user):
                    approver.approval_id.activity_schedule(
                        'approvals.mail_activity_data_approval',
                        user_id=user.id)
                
    def write(self,vals):
        """EOI695 - add updated approvers to chatter

        Args:
            vals (_type_): _description_
        """
        users_before = {}
        if "user_ids" in vals:
            users_before = {record.id: record.user_ids.ids for record in self}
        res = super().write(vals)
        if "user_ids" in vals:
            users_after = {record.id: record.user_ids.ids for record in self}
            for record in self:
                msg = _(f'Level {record.level} updated - ')
                added_users = [
                    user
                    for user in users_after[record.id]
                    if user not in users_before[record.id]
                ]
                if added_users:
                    msg += _("Users Added: ")
                    for user in added_users:
                        msg += f'{self.env["res.users"].browse(user).name}, '
                    msg = msg.strip(", ") + ". "
                removed_users = [
                    user
                    for user in users_before[record.id]
                    if user not in users_after[record.id]
                ]
                if removed_users:
                    msg += _("Users Removed: ")
                    for user in removed_users:
                        
                        msg += f'{self.env["res.users"].browse(user).name}, '
                    msg = msg.strip(", ") + ". "

                if added_users or removed_users:
                    record.approval_id.message_post(body=msg)
        return res

    def unlink(self):
        """EOI695
        """
        if self._context.get("uid") != 1:
            # If user is not sudo it means it is a manual deletion and we must log the change in the chatter
            for record in self:
                if record.user_ids:
                    msg = _(f'Level {record.level} deleted -')
                    for user in record.user_ids:
                        msg += user.name + ", "
                    msg = msg.strip(", ") + ". "
                    record.approval_id.message_post(body=msg)
        return super().unlink()

    @api.model
    def create(self, vals):
        """EOI695 create approval levels
        """
        # if there is a multi approval already, then we want to run this code
        multi_approval_id = vals.get('approval_id')
        multi_approval = self.env["multi.approval"].browse(multi_approval_id) if multi_approval_id else None
        maximum_approval_level = 60
        context = self.env.context
        if not multi_approval or context.get('item') in ['new_bill', 'new_po']:
            return super().create(vals)
        # if no name, add it
        # todo we need to add some kind of name so that we do not encounter an error
        if not vals.get('name'):
            vals['name'] = 'BudgetOwnername'
        # must have user ids
        if not vals.get('user_ids') or not vals['user_ids'][0][2]:
            raise UserError(f'You must add at least one user to the approval')
        # todo is user_id still needed? I think we can remove this field so that we do not need this code
        if not vals.get('user_id'):
            for user in vals['user_ids'][0][2]:
                vals['user_id'] = user
        # user level must be multiple of level 10
        approval_level = vals.get('level')
        if not approval_level:
            raise UserError(f'No approval level for created approval. Please contact the administrator')
        if not approval_level % 10 == 0:
            raise UserError(f'Approval level must be a multiple of level 10. Detected level: {approval_level}')
        # approval level must be higher than the high level on the approval and not greater than 60
        line_levels = [line.level for line in multi_approval.line_ids]
        highest_level = max(line_levels) if line_levels else 0
        if approval_level < highest_level or approval_level > maximum_approval_level:
            raise UserError(f"Approval level must be higher than the highest level on the order {highest_level} and less than the maximum level {maximum_approval_level}. Detected level: {approval_level}")
        # if the approval level is already on the approval form
        if approval_level in line_levels:
            raise UserError(f"The custom approval level {approval_level} already exists on this approval. Please edit the existing level.")
        # status must be set
        if not vals.get('status') or vals['status'] != 'new':
            raise UserError(f'Status must be set as new.')
        # min approval must be at least 1
        min_approval = vals.get('min_approval')
        if not min_approval or min_approval < 1:
            raise UserError(f'Minimum to approve must be at least one')
        return super().create(vals)