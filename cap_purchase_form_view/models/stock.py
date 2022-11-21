# -*- coding: utf-8 -*-
from odoo import fields, models

class StockMove(models.Model):

    _inherit = "stock.move"

    # EOI-426: Part and description should be separated on the PO/PR
    product_name = fields.Char(
        related="product_id.product_tmpl_id.name", string="Product Name"
    )

