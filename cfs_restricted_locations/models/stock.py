# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class RestrictedLocations(models.Model):
    _inherit = 'stock.location'    
    #EOI-290: this field is validate on the ./stock_picking.py file and shown on the form view

    cfs_restricted_location = fields.Boolean(string='Is a restricted by LOT/Serial Location?', 
                                            default=False,
                                            help="Restricted location can only accept one lot/serial number, to set a location as restricted, the location has to be empty or only one lot/serial number")

    @api.model
    def validation_restricted_location(self):
        for rec in self:
            if rec.quant_ids:
                lot_number_to_compare = rec.quant_ids[0].lot_id
                can_be_restricted = True
                for quant in rec.quant_ids:
                  if lot_number_to_compare != quant.lot_id:
                    can_be_restricted = False
                    break
                
                if not can_be_restricted:
                  raise UserError('This location already has more than one lot/serial number \n this can not be a restricted location')

