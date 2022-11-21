from odoo import models, fields, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    wh_type = fields.Selection([('production','Production'),('rd','R&D'),('asset','Asset'),('remote','Remote')], string="Type",
              required='1',default='rd')
    private = fields.Boolean(string='Private', default=False)

    def write(self,vals):

        if vals.get('wh_type',False) and vals.get('wh_type') == 'remote':
            vals['active'] = False
        res = super(StockWarehouse,self).write(vals)
        return res
