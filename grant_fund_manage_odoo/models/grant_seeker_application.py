# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _

class GrantSeekerApplication(models.Model):
    _name = "grant.seeker.application"
    _description = 'Grant Seeker Application'
    _rec_name = 'custom_name'
    # _inherit = ['mail.thread', 'mail.activity.mixin']


    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.env['grant.stages'].search([('fold', '=', False)], order='custom_sequence asc', limit=1).id

    color = fields.Integer(string='Color Index')
    custom_name = fields.Char(
        string='Name',
        required = True
    )
    custom_manager_id = fields.Many2one(
        'res.users',
        string="Responsible",
        required=True
    )
    custom_start_date = fields.Date(
        string="Start Date",
        required = True
    )
    custom_end_date = fields.Date(
        string="End Date",
        required = True
    )
    custom_description = fields.Text(
        string="Description"
    )
    custom_proposal = fields.Html(
        string="Proposal"
    )
    custom_stage_id = fields.Many2one(
        'grant.stages',
        string="Stage",
        ondelete='restrict',
        tracking=True, 
        index=True,
        default=_get_default_stage_id, 
        group_expand='_read_group_stage_ids',
        copy=False
    )
    custom_is_submited_stage = fields.Boolean(
        string="Is Submitted Stage"
    )
    custom_crm_team_id = fields.Many2one(
        'crm.team',
        string="Application Team"
    )
    custom_grant_types_id = fields.Many2one(
        'grant.types',
        string="Grant Type"
    )
    custom_grant_methods_id = fields.Many2one(
        'grant.methods',
        string="Grant Method"
    )
    custom_grant_tags_ids = fields.Many2many(
        'grant.tags',
        string="Grant Tags"
    )
    custom_project_team_id = fields.Many2one(
        'project.project.team',
        string="Project Team"
    )
    custom_company_id = fields.Many2one(
        'res.company',
        required = True,
        default=lambda self: self.env.company,
        string='Company'
    )
    custom_create_date = fields.Date(
        string="Create Date"
    )
    custom_deadline_date = fields.Date(
        string="Deadline Date"
    )
    custom_internal_note = fields.Text(
        string="Internal Notes"
    )
    custom_project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    def custom_grant_tags_print(self):
        str_tags = ''
        for rec in self:
            for tag in self.custom_grant_tags_ids:
                if str_tags == '':
                    str_tags = tag.name
                else:
                    str_tags = str_tags + ' , ' + tag.name
        return str_tags

    def write(self, vals):
        for rec in self:
            if 'custom_stage_id' in vals:
                custom_stage_id = self.env['grant.stages'].browse(vals.get('custom_stage_id'))
                if custom_stage_id.custom_is_submited:
                    vals.update({'custom_is_submited_stage': True})
                else:
                    vals.update({'custom_is_submited_stage': False})
        return super(GrantSeekerApplication, self).write(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('fold', '=', False)]
        order = 'custom_sequence asc'
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def action_view_grant_opportunity(self):
        res_act = self.env.ref('crm.crm_lead_action_pipeline')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('custom_grant_seeker_id', 'in', self.ids)])
        return res_act

    def action_view_grant_sale_order(self):
        res_act = self.env.ref('sale.action_quotations_with_onboarding')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('custom_grant_application_id', 'in', self.ids)])
        return res_act

    def action_view_grant_invoice(self):
        res_act = self.env.ref('account.action_move_out_invoice_type')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('custom_grant_application_id', 'in', self.ids)])
        return res_act

    def action_view_grant_project(self):
        res_act = self.env.ref('project.open_view_project_all')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('custom_grant_seeker_id', 'in', self.ids)])
        return res_act