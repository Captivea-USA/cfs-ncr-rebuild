from odoo import models, fields, api, _

class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    is_hazardous = fields.Boolean(string='Hazardous',related="product_id.is_hazardous")