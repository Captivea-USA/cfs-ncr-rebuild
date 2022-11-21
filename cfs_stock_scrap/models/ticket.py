# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    picking_id = fields.Many2one("stock.picking", string="Origin Picking")
    production_id = fields.Many2one("mrp.production", string="Origin Order")
    return_picking_id = fields.Many2one("stock.picking", string="Return Picking")
    reason_id = fields.Many2one("stock.scrap.reason", string="Scrap Reason")

