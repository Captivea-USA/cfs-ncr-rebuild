from odoo import api, fields, models

class ShippingMethod(models.Model):
    _name = 'res.partner.shipping.method'
    _description = 'Vendor Shipping Method'
    _order = 'name'

    name = fields.Char(string="Name")