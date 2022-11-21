# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    #EOI 443 - Email Acknowledge
    acknowledged = fields.Selection([
        ('waiting', 'Waiting'),
        ('acknowledged', 'Acknowledged'),
        ('denied', 'Denied')
    ], string='Acknowledged',
    default='waiting',
    readonly=True,
    tracking=True)
