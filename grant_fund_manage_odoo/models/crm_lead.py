# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class CRMLead(models.Model):
    _inherit = "crm.lead"

    custom_is_grant_maker = fields.Boolean(
        string="Is Grant Maker",
        copy=True
    )
    custom_is_grant_seeker = fields.Boolean(
        string="Is Grant Seeker",
        copy=True
    )
    custom_grant_seeker_id = fields.Many2one(
        'grant.seeker.application',
        string="Grant Seeker Application",
        copy=True
    )
    custom_proposal = fields.Html(
        string="Proposal",
        copy=True
    )

    def action_view_grant_purchase_order(self):
        res_act = self.env.ref('purchase.purchase_rfq')
        res_act = res_act.sudo().read()[0]
        res_act['domain'] = str([('custom_received_grant_application_id', 'in', self.ids)])
        return res_act

    def action_custom_proposal_send(self):
        self.ensure_one()
        template = self.env.ref('grant_fund_manage_odoo.mail_template_grant_proposal', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='crm.lead',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout='mail.mail_notification_light',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }