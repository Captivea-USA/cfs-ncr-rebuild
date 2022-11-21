# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    helpdesk_ticket_ids = fields.One2many("helpdesk.ticket", "picking_id",string="Helpdesk Tickets")
    helpdesk_return_ticket_ids = fields.One2many("helpdesk.ticket", "return_picking_id",string="Return Helpdesk Tickets")
    ticket_count = fields.Integer(string="Ticket Count", compute="_compute_ticket_count")
    return_ticket_count = fields.Integer(string="Return Ticket Count", compute="_compute_return_ticket_count")
    location_dest_id = fields.Many2one('stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=False, required=True)

    def action_view_tickets(self):
        tickets = self.mapped('helpdesk_ticket_ids')
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        if len(tickets) >= 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        return action

    def action_view_return_tickets(self):
        tickets = self.mapped('helpdesk_return_ticket_ids')
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        if len(tickets) >= 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        return action

    @api.depends('helpdesk_ticket_ids')
    def _compute_ticket_count(self):
        for pick in self:
            pick.ticket_count = len(pick.helpdesk_ticket_ids)
    
    @api.depends('helpdesk_return_ticket_ids')
    def _compute_return_ticket_count(self):
        for pick in self:
            pick.return_ticket_count = len(pick.helpdesk_return_ticket_ids)
