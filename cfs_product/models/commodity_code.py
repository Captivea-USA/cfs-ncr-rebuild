# todo this may be defined elsewhere in our v15 migration
from odoo import models, fields, api
from odoo.exceptions import UserError


class CommodityCode(models.Model):
    _name = "commodity.code"
    _description = "Commodity Code"

    # EOI-387: Add cfs_autoexec module
    # TODO: This domain is commented so it returns as an empty list because we do not 
    # have permissions set up yet. It will need to be updated when we have permissions.
    def _procurement_owner_domain(self):
        return [
        #     (
        #         "id",
        #         "in",
        #         self.env.ref("cfs_product.cfs_group_owner_procurement").users.ids,
        #     )
        ]

    name = fields.Char(string="Name")
    code = fields.Char(string="Commodity Code")
    lead_time = fields.Integer(string="Default Lead Time")
    owner_id = fields.Many2one(
        comodel_name="res.users",
        string="Procurement Owner",
        domain=_procurement_owner_domain,
    )
    code_ids = fields.Many2many(
        comodel_name="product.quality.code", string="Default Quality Codes"
    )

    # EOI - 475 - Prevent Duplicate Commodity Codes
    @api.model
    def create(self, vals):
        commodity_code = self.env['commodity.code'].search([
            ('name', '=', vals.get('name')),
            ('code', '=', vals.get('code')),
            ])
        if commodity_code:
            raise UserError('Commodity code record cannot be created since it is a duplicate of an existing record')
        res = super(CommodityCode, self).create(vals)
        return res

    # EOI - 475 - Prevent Duplicate Commodity Codes
    def write(self, vals):
        if vals.get('name') or vals.get('code'):
            name = vals.get('name') or self.name
            code = vals.get('code') or self.code
            commodity_code = self.env['commodity.code'].search([
                ('name', '=', name),
                ('code', '=', code),
            ])
            if commodity_code:
                raise UserError('Commodity code record cannot be updated since it is a duplicate of an existing record')
        return super(CommodityCode, self).write(vals)
