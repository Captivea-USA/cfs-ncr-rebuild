from odoo import models, fields


class StockWarehouseEnhancement(models.Model):
    _inherit="stock.warehouse"

    #EOI - 349
    wh_type = fields.Selection([
    ('production', 'Production'),
    ('rd', 'R&D'),
    ('asset', 'Asset'),
    ('remote', 'Remote'),
    ], string='Type', required=True, index=True)
    private = fields.Boolean('Private')