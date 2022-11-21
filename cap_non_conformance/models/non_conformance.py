# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class NCR(models.Model):
    _name = 'ncr'
    _description = 'Non Conformance'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    #####################################
    # DEFAULTS
    @api.model
    def _default_cfs_stage_id(self):
        stages = self.env['ncr.stage'].search([])
        sequence = stages[0].sequence
        id = stages[0].id
        for stage in stages:
            if stage.sequence < sequence:
                sequence = stage.sequence
                id = stage.id

        return self.env['ncr.stage'].search([('id', '=', id)], limit=1).id

    @api.model
    def _default_cfs_planned_execution_date(self):
        return datetime.date.today() + datetime.timedelta(days=5)

    #####################################

    # BASE FIELDS
    name = fields.Char('Name', readonly=True, required=False)
    create_date = fields.Datetime('Created On', readonly=True)

    cfs_stage_id = fields.Many2one('ncr.stage', string='Stage', group_expand='_read_group_stage_ids', index=True, tracking=True, readonly=True, store=True, required=False, default=_default_cfs_stage_id)

    # COMPUTED FIELDS
    cfs_ncr_age = fields.Integer('Days Since Creation', compute='_compute_ncr_age')
    cfs_severity_label = fields.Char('Severity Label', compute='_compute_severity_label')

    # RELATIONAL FIELDS
    cfs_assignee_id = fields.Many2one('res.users', string='Assignee', tracking=True)
    cfs_buyer_id = fields.Many2one('res.users', string='Buyer')
    cfs_responsible_engineer_id = fields.Many2one('res.users', string='Responsible Engineer')
    cfs_supplier_id = fields.Many2one('res.partner', string='Supplier')
    cfs_correction_responsible_id = fields.Many2one('res.users', string='Correction Responsible', tracking=True)
    cfs_verification_responsible_id = fields.Many2one('res.users', string='Verification Responsible', tracking=True)
    cfs_financial_notif_id = fields.Many2one('res.users', string='Financial Notification')
    cfs_functional_approver_id = fields.Many2one('res.users', string='Functional Approver')

    # purchase/quality fields
    cfs_part_number_id = fields.Many2one('product.product', string='Part Number')
    cfs_po_num_id = fields.Many2one('purchase.order', string='Purchase Order #')
    cfs_po_line_num_id = fields.Many2one('purchase.order.line', string='PO Line #', domain="[('order_id', '=', cfs_po_num_id)]")
    cfs_lot_sn_id = fields.Many2one('stock.production.lot', string='Lot/Serial', domain="[('product_id', '=', cfs_part_number_id)]")
    cfs_quality_check_id = fields.Many2one('quality.check', string='Quality Check')

    # manufacturing fields
    cfs_mo_id = fields.Many2one('mrp.production', string='Manufacturing Order')

    cfs_location_id = fields.Many2one('ncr.location', string='Location')
    cfs_source_id = fields.Many2one('ncr.source', string='Source')
    cfs_reason_id = fields.Many2one('ncr.reason', string='Reason Code')
    cfs_severity_id = fields.Many2one('ncr.severity', string='Severity Level', tracking=True)
    cfs_disposition_id = fields.Many2one('ncr.disposition', string='Disposition', tracking=True)
    cfs_sme_ids = fields.One2many('ncr.sme', 'cfs_ncr_id', string='SME')
    cfs_type_id = fields.Many2one('ncr.type', string='Type')
    
    # NUMBER FIELDS
    cfs_qty_tested = fields.Integer('QTY Tested')
    cfs_qty_failed = fields.Integer('QTY Failed')
    cfs_part_value = fields.Float('Part Value')
    cfs_disposition_cost = fields.Float(string='Disposition Cost in $', tracking=True)
    cfs_internal_labor_hrs = fields.Float(string='Internal Labor Hours', tracking=True)

    # DATE FIELDS
    cfs_planned_execution_date = fields.Date('Planned Execution Date', tracking=True, default=_default_cfs_planned_execution_date)

    # CHAR FIELDS
    cfs_lot_sn_name = fields.Char(string='Lot/Serial Name')
    cfs_nc_description = fields.Html(string='NC Description')
    cfs_disposition_notes = fields.Html(string='Disposition Notes')
    cfs_justification_notes = fields.Html(string='Justification Notes')
    cfs_correction_notes = fields.Html(string='Correction Notes')
    cfs_verification_notes = fields.Html(string='Verification Notes')
    
    #####################################
    # COMPUTED FIELDS
    @api.depends('cfs_ncr_age')
    def _compute_ncr_age(self):
        for record in self:
            today = datetime.datetime.today()
            delta = (today - record.create_date)
            record.cfs_ncr_age = delta.days

    @api.depends('cfs_severity_label')
    def _compute_severity_label(self):
        for record in self:
            if record.cfs_severity_id:
                record.cfs_severity_label = record.cfs_severity_id.name
            else:
                record.cfs_severity_label = False
    #####################################

    #####################################
    # ACTIONS
    def advance_stage(self):
        self.cfs_stage_id = self.cfs_stage_id.id + 1
        return True

    def pass_ncr(self):
        if self.env.user.id != self.cfs_functional_approver_id.id:
            raise UserError('You are not allowed to approve this NCR!')
        else:
            self.cfs_stage_id = 4
        return True

    def fail_ncr(self):
        if self.env.user.id != self.cfs_functional_approver_id.id:
            raise UserError('You are not allowed to deny this NCR!')
        else:
            self.cfs_stage_id = 2
        return True
    #####################################

    def scheduled_activity(self, summary, date, user):
        notify_type = self.env.ref("mail.mail_activity_data_todo", False)
        self.env['mail.activity'].create({
                'summary': summary,
                'date_deadline': date,
                'user_id': user,
                'res_id':self.id,
                'automated':True,
                'res_model_id': self.env['ir.model']._get(self._name).id,
                'activity_type_id':notify_type.id
            }) 

    def notification_logic(self, vals):
        #Scheduled activities on updated fields
        if vals.get('cfs_assignee_id'):
            user = vals.get('cfs_assignee_id')
            summary = 'An NCR has been assigned to you.'
            date = datetime.date.today() + datetime.timedelta(days=3)
            self.scheduled_activity(summary, date, user)
        # If stage is released from draft
        if (vals.get('cfs_stage_id') == 2) and (self.cfs_stage_id.id == 1) and (vals.get('cfs_severity_id') != 4):
            # users = self.env['res.users'].search([('id', 'in', [self.cfs_responsible_engineer_id.id, self.cfs_buyer_id.id, self.cfs_part_number_id.responsible_id.id])],limit=3)
            users = [self.cfs_responsible_engineer_id.id, self.cfs_buyer_id.id, self.cfs_part_number_id.responsible_id.id]
            for user in users:
                if user:
                    summary = 'You have been referenced on a recently Released NCR.'
                    date = datetime.date.today() + datetime.timedelta(days=3)
                    self.scheduled_activity(summary, date, user)
        return True

    @api.model
    def create(self, vals):
        seq_date = None
        if 'create_date' in vals:
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['create_date']))
        seq_number = self.env['ir.sequence'].next_by_code('ncr', sequence_date=seq_date) or ('New')
        year = datetime.datetime.now().strftime('%y')
        vals['name'] =  'NCR/{}/{}'.format(year, seq_number)
        # self.notification_logic(vals)

        result = super(NCR, self).create(vals)
        return result
    
    def write(self, vals):
        #Track NC Description
        if vals.get('cfs_nc_description'):
            msg = _('NC Description: %(old_value)s --> %(new_value)s', old_value=self.cfs_nc_description, new_value=vals.get('cfs_nc_description'))
            self.message_post(body=msg)

        # self.notification_logic(vals)
        
        result = super(NCR, self).write(vals)
        return result

    

    # This is to keep the ncr stages open even if empty
    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['ncr.stage'].search([])
        return stage_ids

    #Send notifications daily as a digest
    # def _cron_send_digest_email(self):
    #     return True

    #####################################
    # ON CHANGE
    @api.onchange('cfs_po_num_id')
    def _onchange_cfs_po_num_id(self):
        for rec in self:
            rec['cfs_supplier_id'] = rec.cfs_po_num_id.partner_id.id
            rec['cfs_buyer_id'] = rec.cfs_po_num_id.cfs_buyer.id

    @api.onchange('cfs_part_number_id')
    def _onchange_cfs_part_number_id(self):
        for rec in self:
            rec['cfs_responsible_engineer_id'] = rec.cfs_part_number_id.design_owner.id
            rec['cfs_part_value'] = rec.cfs_part_number_id.list_price
    
    #####################################




class Stage(models.Model):
    _name = "ncr.stage"
    _description = "NCR Stages"
    _rec_name = 'name'
    _order = "sequence, id, name"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage. It will appear as a tooltip over the stage's name.")
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')

class NCRType(models.Model):
    _name = 'ncr.type'
    _description = 'Non Conformance Types'

    name = fields.Char('Type', required=True, readonly=False)
    cfs_use_when = fields.Char('Use When')

class NCRLocation(models.Model):
    _name = 'ncr.location'
    _description = 'Non Conformance Locations'

    name = fields.Char('Location', required=True, readonly=False)

class NCRSource(models.Model):
    _name = 'ncr.source'
    _description = 'Non Conformance Source'

    name = fields.Char('Source', required=True, readonly=False)

class NCRReason(models.Model):
    _name = 'ncr.reason'
    _description = 'Non Conformance Reason'

    name = fields.Char('Reason Code', required=True, readonly=False)

class NCRSeverity(models.Model):
    _name = 'ncr.severity'
    _description = 'Non Conformance Severity'

    name = fields.Char('Severity', required=True, readonly=False)

    cfs_severity_code = fields.Char('Severity Code')
    cfs_description = fields.Char('Description')

class NCRDisposition(models.Model):
    _name = 'ncr.disposition'
    _description = 'Non Conformance Dispositions'

    name = fields.Char('Disposition', required=True, readonly=False)

    cfs_description = fields.Char('Description')

class NCRSME(models.Model):
    _name = 'ncr.sme'
    _description = 'Non Conformance SME'

    # name = fields.Char('Name', required=True, readonly=False)

    cfs_user_id = fields.Many2one('res.users', string='SME')
    cfs_notes = fields.Text('Note')
    cfs_attachment = fields.Binary('Attachment')
    cfs_ncr_id = fields.Many2one('ncr', string='NCR')


    @api.model
    def create(self, vals):
        notify_type = self.env.ref("mail.mail_activity_data_todo", False)
        
        user = vals.get('cfs_user_id')
        ncr = self.cfs_ncr_id
        ncr_id = vals.get('cfs_ncr_id')
        #Notify the SMEs when they are assigned to a NCR
        self.env['mail.activity'].create({
            'summary':'You have been assigned to a NCR.',
            'date_deadline':datetime.date.today() + datetime.timedelta(days=1),
            'user_id': user,
            'res_id':ncr_id,
            'automated':True,
            'res_model_id': self.env['ir.model']._get(ncr._name).id,
            'activity_type_id':notify_type.id
        })   
        result = super(NCRSME, self).create(vals)
        return result
