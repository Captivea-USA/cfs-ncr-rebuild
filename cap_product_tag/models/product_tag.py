# -*- coding: utf-8 -*-
from odoo import models, fields
from random import randint

class ProductTags(models.Model):
    _name = "product.tag"
    _description = "Buyer Category"

    def _get_default_color(self):
        return randint(1, 11)

    # TODO `buyer` needs a domain to show only Buyer group members. This must be updated after permissions are implemented.
    buyer_id = fields.Many2one("res.users", string="Buyer")
    active = fields.Boolean(string="Active", default=True, help="The active field allows you to hide the category without removing it.")
    color_index = fields.Integer(string="Color Index", default=_get_default_color)
    name = fields.Char(string="Category",index=True, required=True)
    parent_category = fields.Many2one('product.tag', string='Parent Category', index=True, ondelete='cascade')
    approved_vendors = fields.Many2many("res.partner", string="Approved Vendors")
    default_purchase_account = fields.Many2one("account.account", string="Default Purchase Account")

    
    def name_get(self):
        if self._context.get('partner_category_display') == 'short':
            return super(ProductTags, self).name_get()
        res = []
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name)
                current = current.parent_category
            res.append((category.id, ' / '.join(reversed(names))))
        return res