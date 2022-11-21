from odoo import fields, models


class ProductQualityCode(models.Model):
    _name = "product.quality.code"
    _description = "Quality Codes"

    name = fields.Char(string="Name", required=True)
