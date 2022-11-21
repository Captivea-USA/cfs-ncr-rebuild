from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # is_hazardous = fields.Boolean(string='Hazardous',compute="_compute_hazardous_product", store=True)
    is_hazardous = fields.Boolean(string="Hazardous")
    rma = fields.Char(string="RMA")



