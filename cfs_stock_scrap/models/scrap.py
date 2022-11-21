# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    helpdesk_ticket_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket")
    reason_id = fields.Many2one("stock.scrap.reason", string="Scrap Reason")
    lot_ids = fields.Many2many('stock.production.lot', compute='_compute_lot_ids', string='Serial Numbers')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial', states={'done': [('readonly', True)]}, domain="[('product_id', '=', product_id),('company_id', '=', company_id),('id', 'in', lot_ids)]", check_company=True)

    @api.depends("picking_id")
    def _compute_lot_ids(self):
        for scrap in self:
            lots = []
            for mvl in scrap.picking_id.move_line_ids_without_package:
                if mvl.lot_id:
                    lots.append(mvl.lot_id.id)
            scrap.lot_ids = lots

    def action_validate(self):
        return_picking_id = False
        product_name = '/'
        if self.reason_id:
            # Warehouse Transfer
            if self.picking_id:
                for line in self.picking_id.move_ids_without_package.filtered(lambda l: l.product_id.id == self.product_id.id):
                    if self.picking_id.state != 'done' and self.scrap_qty > line.reserved_availability:
                        raise UserError(_("You don't have this many to scrap!"))
                    else:
                        product_name = line.name
            # Manufacturing Order
            if self.production_id:
                for line in self.production_id.move_raw_ids.filtered(lambda l: l.product_id.id == self.product_id.id):
                    if self.production_id.state != 'done' and self.scrap_qty > line.forecast_availability:
                        raise UserError(_("You don't have this many to scrap!"))
                    else:
                        product_name = line.name

            internal_transfer_operation = self.picking_id and self.picking_id.picking_type_id.warehouse_id.int_type_id or \
                                          self.production_id and self.production_id.picking_type_id.warehouse_id.int_type_id

            if internal_transfer_operation:
                return_picking_id = self.env['stock.picking'].create({
                        "location_id": self.scrap_location_id.id,
                        "location_dest_id": self.location_id.id,
                        "picking_type_id": internal_transfer_operation.id,
                        "move_ids_without_package": [(0, 0, {
                            "product_id": self.product_id.id,
                            "name": product_name,
                            "product_uom": self.product_id.uom_id.id,
                            "product_uom_qty": self.scrap_qty,
                            "reserved_availability": 0,
                            "procure_method": 'make_to_stock',
                        })]
                })
                return_picking_id.action_confirm()

        source_name = self.picking_id and self.picking_id.name or self.production_id and self.production_id.name or False

        helpdesk_ticket_id = self.env["helpdesk.ticket"].create({
            "name": "{} - {}".format(self.product_id.name, source_name or 'No Transfer'),
            "picking_id": self.picking_id and self.picking_id.id or False,
            "production_id": self.production_id and self.production_id.id or False,
            "return_picking_id": return_picking_id and return_picking_id.id,
            "reason_id": self.reason_id.id,
            "team_id": self.env["helpdesk.team"].search([("name", "=", "Material Review")]).id,
        })

        res = super(StockScrap, self).action_validate()

        for scrap in self:
            scrap.write({
                "helpdesk_ticket_id": helpdesk_ticket_id.id
            })

        return res
