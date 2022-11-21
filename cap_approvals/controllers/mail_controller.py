# -*- coding: utf-8 -*-

from odoo import http

class ButtonAcknowledgement(http.Controller):
    #EOI 443 - Email Acknowledge
    @http.route('/acknowledgement/<answer>/<model>/<int:id>', auth='public', website=True)
    def email_acknowledged(self, answer, model, id):
        """
        EOI - 431 - Email Approver Logic
        erprod156 - test if user is able to access portal
        """
        if answer in ['acknowledged', 'denied']:
            model_name = model.replace('_', '.')
            record = http.request.env[model_name].sudo().browse(id)
            if not http.request.env.user._is_public():
                record.sudo().acknowledged = answer
                yes_or_no = 'YES' if answer == 'acknowledged' else ('NO' if answer == 'denied' else 'UNDEFINED')
                return http.request.render('cap_approvals.template_response_recorded', {
                    'answer': yes_or_no,
                })
            base_url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            return http.request.render('cap_approvals.template_unknown_user', {
                'base_url': base_url
            })
