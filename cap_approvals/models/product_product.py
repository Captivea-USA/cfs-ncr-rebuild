from odoo import fields, api, models, _

class Product(models.Model):
    _inherit = 'product.product'

    # EOI-349: Adding for approver logic
    design_owner = fields.Many2one('res.users', string="Design Owner")