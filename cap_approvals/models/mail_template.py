# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailTemplate(models.Model):
    _inherit = "mail.template"
    
    #EOI 443 - Email Acknowledge
    include_acknowledgement = fields.Boolean(string='Include Acknowledgement')


