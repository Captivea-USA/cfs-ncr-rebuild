# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

APPROVED = 10
REFUSED = 6
CFO_MIN_AMOUNT = 50000

class MultiApproval(models.Model):
    _name = 'multi.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # EOI-532: Multi Approval description typos
    _description = 'Multi Approval'

    # EOI-349: Adding views to replicate UAT v14
    amount = fields.Float(string="Amount")
    location = fields.Char(string="Location")

    code = fields.Char(default=_('New'))
    name = fields.Char(string='Title', required=True)
    user_id = fields.Many2one(
        string='Request by', comodel_name="res.users",
        required=True, default=lambda self: self.env.uid)
    priority = fields.Selection(
        [('0', 'Normal'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority', default='0')
    request_date = fields.Datetime(
        string='Request Date', default=fields.Datetime.now)
    complete_date = fields.Datetime()
    type_id = fields.Many2one(
        string="Type", comodel_name="multi.approval.type", required=True)
    image = fields.Binary(related="type_id.image")
    description = fields.Html('Description')
    state = fields.Selection(
        [('Draft', 'Draft'),
         ('Submitted', 'Submitted'),
         ('Approved', 'Approved'),
         ('Refused', 'Refused'),
         ('Cancel', 'Cancel')], default='Draft', tracking=True)

    document_opt = fields.Selection(
        string="Document opt",
        readonly=True, related='type_id.document_opt')
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')

    contact_opt = fields.Selection(
        string="Contact opt",
        readonly=True, related='type_id.contact_opt')
    contact_id = fields.Many2one('res.partner', string='Contact')

    date_opt = fields.Selection(
        string="Date opt",
        readonly=True, related='type_id.date_opt')
    date = fields.Date('Date')

    period_opt = fields.Selection(
        string="Period opt",
        readonly=True, related='type_id.period_opt')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

    item_opt = fields.Selection(
        string="Item opt",
        related='type_id.item_opt')
    item_id = fields.Many2one('product.product', string='Item')

    multi_items_opt = fields.Selection(
        string="Multi Items opt",
        readonly=True, related='type_id.multi_items_opt')
    item_ids = fields.Many2many('product.product', string='Items')

    quantity_opt = fields.Selection(
        string="Quantity opt",
        readonly=True, related='type_id.quantity_opt')
    quantity = fields.Float('Quantity')

    amount_opt = fields.Selection(
        string="Amount opt",
        readonly=True, related='type_id.amount_opt')
    amount = fields.Float('Amount')

    payment_opt = fields.Selection(
        string="Payment opt",
        readonly=True, related='type_id.payment_opt')
    payment = fields.Float('Payment')

    reference_opt = fields.Selection(
        string="Reference opt",
        readonly=True, related='type_id.reference_opt')
    reference = fields.Char('Reference')

    location_opt = fields.Selection(
        string="Location opt",
        readonly=True, related='type_id.location_opt')
    location = fields.Char('Location')
    line_ids = fields.One2many('multi.approval.line', 'approval_id',
                               string="Lines")
    line_id = fields.Many2one('multi.approval.line', string="Line", copy=False)
    deadline = fields.Date(string='Deadline', related='line_id.deadline')
    pic_id = fields.Many2one(
        'res.users', string='Approver', related='line_id.user_id')
    is_pic = fields.Boolean(compute='_check_pic')
    follower = fields.Text('Following Users', default='[]', copy=False)

    # copy the idea of hr_expense
    attachment_number = fields.Integer(
        'Number of Attachments', compute='_compute_attachment_number')

    # EOI-349: User_status used as a parameter for the invisible attribute
    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status", default="new")
    
    # EOI-349: Many2one to purchase.order required by smart button
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    multi_approval_notes = fields.Text(string="Notes")

    # EOI-349: Computes user_status
    # EOI-552/559: Adapted logic to encompass multiple users on per line
    @api.depends('line_ids.status')
    def _compute_user_status(self):
        for rec in self:
            for line in rec.line_ids:
                if self.env.user.id in line.user_ids.ids: 
                    rec.user_status = line.status  
            # EOI598: if user status wasn't set, set it to False
            if not rec.user_status:
                rec.user_status = False

    # EOI-349: Retrieves Approver IDs and Passes data into Create
    def update_approver_ids(self,res_id,req,total,model_name,budget):

        # Retrive Request from AM and Approver Data
        if model_name == 'account.move':
            cfo = self.env["ir.config_parameter"].sudo().get_param("cap_settings.cfs_cfo")
            try:
                cfo = int(cfo)
            except:
                raise UserError(f'Unable to convert cfs_cfo {cfo} to integer. Please check the value of CFO under Budget User Parameter in settings.')
            # EOI524 budget owner should be of type analytic account
            budget_owner = budget.user_id.id
            vals = []
            # EOI502 - redo bill approval logic to add the cfo as another level
            if budget_owner:
                # Add Budget Owner
                vals.append({
                    'user_ids': [(4, budget_owner, 0)],
                    'name': 'BudgetOwnername',
                    'everyone_approves': True,
                    'min_approval': 1,
                    'level': 10,
                    'sequence':10,
                    'require_opt': 'Optional',
                    'user_id': budget_owner,
                    'approval_id': req.id,
                    'status': 'new'
                })

            if total > CFO_MIN_AMOUNT:
                # Add CFO
                vals.append({
                    'user_ids': [(4, cfo, 0)],
                    'name': 'CFOname',
                    'everyone_approves': True,
                    'min_approval': 1,
                    'level': 20,
                    'sequence':20,
                    'require_opt': 'Optional',
                    'user_id': cfo,
                    'approval_id': req.id,
                    'status': 'new'
                })
            # Create all approval lines
            for val in vals:
                self.env['multi.approval.line'].with_context({'item': 'new_bill'}).create(val)
        # Retrive Request from PO and Approver Data
        elif model_name == 'purchase.order':
            po = self.env['purchase.order'].browse(res_id)
            vals,message_list = po.get_approver_vals(req,total)
            # eoi591 show in chatter who was deleted
            for message in message_list:
                req.message_post(body=message)
            # Creates Lines under the Multi Level Approval Request
            for val in vals:
                self.env['multi.approval.line'].with_context({'item': 'new_bill'}).create(val)

    # EOI-349: Apart to update the color of the tag for the "Done" field
    def _update_tags(self, color=None):
        """Adds a red tag (refused) for the current approval level with the current user."""
        # raise UserError (str(self))
        # for req in self:
        
        current_approval = self._get_current_approval()
        # raise UserError(str(current_approval.id))
        if current_approval:
            user_tag = self.line_ids.user_approval_ids.filtered(lambda tag: tag.user_id == self.env.user)
            # raise UserError(str(user_tag))
            if user_tag:
                if not color:
                    user_tag.unlink()
                else:
                    user_tag.write({'color': color})
            else:
                self.env['user.approval.tags'].create({'user_id': self.env.user.id,
                                                        'color': color,
                                                        'request_level_id': current_approval.id})

        self._compute_level_status()

    # EOI-349: Finds current approval request for _update_tags function
    def _get_current_approval(self, user=None):
        self.ensure_one()
        if not user:
            user = self.env.user

        return self.line_ids.filtered(lambda approver: user in approver.user_ids)
                                                           

    # EOI-349: Checks if status of the line
    @api.depends('user_approval_ids')
    def _compute_level_status(self):
        for request in self:
            # If the request is cancelled, all levels are cancelled
            for line in request.line_ids:
                if line.status == 'cancel':
                    line.write({'status': 'cancel'})
                    continue

            last_level_approved = True
            for level in request.line_ids.sorted(key=lambda a: a.level):
                if level.is_level_approved():
                    status = 'approved'
                    # EOI575 - remove pening activities
                    for user in level.mapped("user_ids"):
                        self.sudo()._get_user_approval_activities(user=user).unlink()
                elif level.is_level_refused():
                    status = "refused"
                    last_level_approved = False
                elif last_level_approved:
                    status = 'pending'
                    last_level_approved = False
                else:
                    status = 'new'

                level.status = status

    # EOI-349: Needed to create activities
    def _get_user_approval_activities(self, user):
            domain = [
                ('res_model', '=', 'multi.approval'),
                ('res_id', 'in', self.ids),
                ('activity_type_id', '=', self.env.ref('approvals.mail_activity_data_approval').id),
                ('user_id', '=', user.id)
            ]
            activities = self.env['mail.activity'].search(domain)
            # raise
            return activities

    # EOI-349: Adding in Withdrawal Logic
    def action_withdraw(self, approver=None):
        current_user_approval = self.line_ids.filtered(lambda approver: self.env.user in approver.user_ids)
        # raise UserError(str(current_user_approval.level))
        if not current_user_approval:
            raise UserError("You do not have any approval to withdraw.")
        if self.state != 'Submitted':
            raise UserError("The request must be in Submitted stage to withdraw your approval.")
        index = 0 
        # User level is the same as the current request level
        for line in self.line_ids:
            next_index = index + 1
            if current_user_approval.level == line.level:
                try:
                    # 'Out of Index' error should not happen, because once the last person on the lines approves: the request state will advance to 'Approved' or 'Refused'
                    # Which would prevent user from hitting 'Withdraw' due to the 2nd if statement
                    if self.line_ids[next_index]: 
                        if self.line_ids[next_index].status == 'pending':
                            self._update_tags()  # Remove tag for this user
                            line.status = 'pending' # Changes current user's status from 'approved' to 'pending'
                            self.line_ids[next_index].status = 'new'
                            line.action_timestamp = datetime.now()
                            index += 1       
                        elif self.line_ids[next_index].status != 'pending':
                            raise UserError("You cannot withdraw your approval because users from higher levels have already approved the request.")
                except:
                    raise UserError("How did you even get here?") 
            else:
                index += 1


    def _check_pic(self):
        for r in self:
            r.is_pic = r.pic_id.id == self.env.uid

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'multi.approval'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count'])
                          for data in attachment_data)
        for r in self:
            r.attachment_number = attachment.get(r.id, 0)

    def action_cancel(self, confirm=True):
        """EOI377 also put the PO into a state of reapproval so that it can be resubmitted
        """
        # todo self and recs are the same thing so why do we need a lambda function
        # todo this code seems to be part of the third party app and not customized
        recs = self.filtered(lambda x: x.state == 'Draft' or x.state == 'Submitted')
        # if the cancel is first clicked, we'll send the confirmation dialog
        if confirm:
            message = f"Are you sure you want to cancel {recs.name}? The approval will need to recreated from scratch if it is to be recreated."
            # delete previous message
            query ='delete from confirm_dialog'
            self.env.cr.execute(query)
            # create new dialog with the approval id so that we can send it back through
            value = self.env['confirm.dialog'].sudo().create(
                {'approval_id': recs.id, 'text':message}
            )
            return{
                'type':'ir.actions.act_window',
                'name':'Confirm Cancelation',
                'res_model':'confirm.dialog',
                'view_mode':'form',
                'target':'new',
                'res_id':value.id                
            }
        # todo get pending activities and cancel
        recs.write({'state': 'Cancel'})
        msg = _(f'{self.name} has been canceled so the PO must be resubmitted for approval.')
        recs.finalize_activity_or_message('canceled', msg)
        self.update_po_state_reapprove()

    # EOI-349: Overrided the 3rd party function to kick start the Approval Logic
    def action_submit(self):
        recs = self.filtered(lambda x: x.state == 'Draft')
        self.state = 'Submitted'
        for line in self.line_ids:
            if line == self.line_ids[0]:
                line.status = 'pending'
                line.sudo()._create_activity()
                
        recs.send_request_mail()
        recs.send_activity_notification()

    @api.model
    def get_follow_key(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        k = '[res.users:{}]'.format(user_id)
        return k

    def update_follower(self, user_id):
        self.ensure_one()
        k = self.get_follow_key(user_id)
        follower = self.follower
        if follower and k not in follower:
            self.follower = follower + k

    # 13.0.1.1
    def set_approved(self):
        self.ensure_one()
        self.state = 'Approved'
        self.complete_date = fields.Datetime.now()
        self.send_approved_mail()

    def set_refused(self, reason=''):
        self.ensure_one()
        self.state = 'Refused'
        self.complete_date = fields.Datetime.now()
        self.send_refused_mail()

    # EOI-349: Overhaul on logic to incorporate CFS Approval Logic
    # EOI-559/552: Adapted Logic to Encompass multiple user_ids per line
    def action_approve(self):
        recs = self.filtered(lambda x: x.state == 'Submitted')
        for rec in recs:
            # Update follower
            rec.update_follower(self.env.uid)

            msg = _('I approved')
            rec.finalize_activity_or_message('approved', msg)
            index = 0
            for line in rec.line_ids:
                next_index = index + 1 
                if line.status != 'pending' and self.env.user.id in line.user_ids.ids:
                    raise UserError('You cannot approve the request until all the required users from lower levels approve it.')

                if self.env.user.id in line.user_ids.ids and line.status != 'approved':

                    line.status = 'approved'
                    line.action_timestamp = datetime.now()
                    try:
                        if rec.line_ids[next_index]:
                            index += 1
                            rec.line_ids[next_index].status = 'pending'
                            rec.line_ids[next_index].sudo()._create_activity()

                    # When we go out of index, we can advance from Submitted -> Approved
                    except:
                        rec.state = 'Approved'
                        po = self.env['purchase.order'].search([('name','ilike',self.reference)])
                        po.state = 'approved'
                else: 
                    index += 1
            self._update_tags(APPROVED)

    # EOI-349: Update PO state to 'to reapprove'
    def update_po_state_reapprove(self):
        po = self.env['purchase.order'].search([('name','ilike',self.reference)])
        po.state = 'to reapprove'

    # EOI-349: Overhaul on logic to incorporate CFS Refusal Logic
    def action_refuse(self, reason=''):
        recs = self.filtered(lambda x: x.state == 'Submitted')
        for rec in recs:

            # Update follower
            rec.update_follower(self.env.uid)

            msg = _('I refused')
            rec.finalize_activity_or_message('refused', msg)
            for line in rec.line_ids:
                for user_id in line.user_ids:
                    if line.status != 'pending' and user_id.name == self.env.user.name:
                        raise UserError('You cannot approve the request until all the required users from lower levels approve it.')

                    if user_id.id == self.env.user.id and line.status != 'approved':
                        line.status = 'refused'
                        line.action_timestamp = datetime.now()
                    # Update record state to reflect refusal
                    rec.state = 'Refused'
                    # EOI575 - remove pening activities
                    self.sudo()._get_user_approval_activities(user=user_id).unlink()
                    self.update_po_state_reapprove()
            self._update_tags(REFUSED)

    def finalize_activity_or_message(self, action, msg):
        requests = self.filtered(
            lambda r: r.type_id.activity_notification
        )
        notify_type = self.env.ref("mail.mail_activity_data_todo", False)
        if requests and notify_type: 
            activities = requests.mapped("activity_ids").filtered(
                lambda a: a.activity_type_id == notify_type and a.user_id == self.env.user)
            activities._action_done(msg)

        requests2 = self - requests
        if requests2:
            requests2.message_post(body=msg)

    def _create_approval_lines(self):
        ApprovalLine = self.env['multi.approval.line']
        self.context()
        for r in self:
            lines = r.type_id.line_ids.sorted('sequence')
            last_seq = 0
            for l in lines:
                line_seq = l.sequence
                if not line_seq or line_seq <= last_seq:
                    line_seq = last_seq + 1
                last_seq = line_seq
                vals = {
                    'name': l.name,
                    'user_id': l.get_user(),
                    'sequence': line_seq,
                    'require_opt': l.require_opt,
                    'approval_id': r.id
                }
                if l == lines[0]:
                    vals.update({'state': 'Waiting for Approval'})
                approval = ApprovalLine.with_context({'item': 'new_po'}).create(vals)
                if l == lines[0]:
                    r.line_id = approval
    @api.model
    def create(self, vals):
        seq_date = vals.get('request_date', fields.Datetime.now())
        vals['code'] = self.env['ir.sequence'].next_by_code(
            'multi.approval', sequence_date=seq_date) or _('New')
        result = super(MultiApproval, self).create(vals)
        return result

    # 12.0.1.3
    def send_request_mail(self):
        requests = self.filtered(
            lambda r: r.type_id.mail_notification and r.pic_id and
                r.state == 'Submitted'
        )
        for req in requests:
            if req.type_id.mail_template_id:
                req.type_id.mail_template_id.send_mail(req.id)
            else:
                message = self.env['mail.message'].create({
                    'subject': _('Request the approval for: {request_name}').format(
                        request_name=req.display_name
                    ),
                    'model': req._name,
                    'res_id': req.id,
                    'body': self.description,
                })

                self.env['mail.mail'].sudo().create({
                    'mail_message_id': message.id,
                    'body_html': self.description,
                    'email_to': req.pic_id.email,
                    'email_from': req.user_id.email,
                    'auto_delete': True,
                    'state': 'outgoing',

                })

    def send_approved_mail(self):
        requests = self.filtered(
            lambda r: r.type_id.approve_mail_template_id and
                r.state == 'Approved'
        )
        for req in requests:
            req.type_id.approve_mail_template_id.send_mail(req.id)

    def send_refused_mail(self):
        requests = self.filtered(
            lambda r: r.type_id.refuse_mail_template_id and
                r.state == 'Refused'
        )
        for req in requests:
            req.type_id.refuse_mail_template_id.send_mail(req.id)

    def send_activity_notification(self):
        requests = self.filtered(
            lambda r: r.type_id.activity_notification and r.pic_id and
                r.state == 'Submitted'
        )
        notify_type = self.env.ref("mail.mail_activity_data_todo", False)
        if not notify_type:
            return
        for req in requests:
            summary = _("The request {code} need to be reviewed").format(
                code=req.code
            )
            self.env['mail.activity'].create({
                'res_id': req.id,
                'res_model_id': self.env['ir.model']._get(req._name).id,
                'activity_type_id': notify_type.id,
                'summary': summary,
                'user_id': req.pic_id.id,
            })   
