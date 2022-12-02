# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast

from datetime import datetime

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.osv.expression import OR

class QualityPoint(models.Model):
    _inherit = "quality.point"
    
    quality_clause = fields.Many2one("product.quality.code", "Quality Clause")

    @api.model
    def _get_domain(self, product_ids, picking_type_id, measure_on='operation'):
        """ Helper that returns a domain for quality.point based on the products and picking type
        pass as arguments. It will search for quality point having:
        - No product_ids and no product_category_id
        - At least one variant from product_ids
        - At least one category that is a parent of the product_ids categories

        :param product_ids: the products that could require a quality check
        :type product: :class:`~odoo.addons.product.models.product.ProductProduct`
        :param picking_type_id: the products that could require a quality check
        :type product: :class:`~odoo.addons.stock.models.stock_picking.PickingType`
        :return: the domain for quality point with given picking_type_id for all the product_ids
        :rtype: list
        """
        
        domain = [('picking_type_ids', 'in', picking_type_id.ids)]
        domain_in_products_or_categs = ['|', ('product_ids', 'in', product_ids.ids), ('product_category_ids', 'parent_of', product_ids.categ_id.ids)]
        domain_no_products_and_categs = [('product_ids', '=', False), ('product_category_ids', '=', False)]
        domain += OR([domain_in_products_or_categs, domain_no_products_and_categs])
        domain += [('measure_on', '=', measure_on)]
        #CFS Ticket
        domain += [('quality_clause', '=', False)]

        return domain

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals_list):
        mls = super(StockMoveLine, self).create(vals_list)
        mls._filter_move_lines_applicable_for_quality_check()._create_check()

        #CFS Ticket
        for ml in mls:
            ml_clauses = ml.move_id.purchase_line_id.cfs_quality_codes
            ml_picking = ml.move_id.picking_type_id.id
            if ml_clauses:
                quality_points = self.env['quality.point'].sudo().search(['&',('quality_clause','in', ml_clauses.ids),('picking_type_ids','in', ml_picking)])
                check_values_list = []
                for quality_point in quality_points:
                    if quality_point.check_execute_now():
                        check_values = ml._get_check_values(quality_point)
                        check_values_list.append(check_values)
                if check_values_list:
                    self.env['quality.check'].sudo().create(check_values_list)

        return mls
