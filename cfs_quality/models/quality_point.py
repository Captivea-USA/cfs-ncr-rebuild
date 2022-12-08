# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast

from datetime import datetime
from collections import defaultdict

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
        #CFS Ticket [ERPQ4-284]
        domain += [('quality_clause', '=', False)]

        return domain

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals_list):
        mls = super(StockMoveLine, self).create(vals_list)
        mls._filter_move_lines_applicable_for_quality_check()._create_check()
        #CFS Ticket [ERPQ4-284]
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

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _create_quality_checks(self):
        # Groupby move by picking. Use it in order to generate missing quality checks.
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        check_vals_list = []
        for move in self:
            if move.picking_id:
                pick_moves[move.picking_id] |= move
        for picking, moves in pick_moves.items():
            quality_points_domain = self.env['quality.point']._get_domain(moves.product_id, picking.picking_type_id, measure_on='operation')
            quality_points = self.env['quality.point'].sudo().search(quality_points_domain)
            #CFS Ticket [ERPQ4-284]
            #create the base odoo points if applicable
            if quality_points:
                picking_check_vals_list = quality_points._get_checks_values(moves.product_id, picking.company_id.id, existing_checks=picking.sudo().check_ids)
                for check_value in picking_check_vals_list:
                    check_value.update({
                        'picking_id': picking.id,
                    })
                check_vals_list += picking_check_vals_list
            #create the quality clause depending points
            for mls in moves.move_line_ids:
                for ml in mls:
                    ml_clauses = ml.move_id.purchase_line_id.cfs_quality_codes
                    ml_picking = ml.move_id.picking_type_id.id
                    if ml_clauses:
                        quality_points = self.env['quality.point'].sudo().search(['&',('quality_clause','in', ml_clauses.ids),('picking_type_ids','in', ml_picking)])
                        checks_already_made = self.env['quality.check'].sudo().search(['&',('move_line_id','=',ml.id),('point_id','in',quality_points.ids)])
                        if not checks_already_made:
                            clause_check_values_list = []
                            for quality_point in quality_points:
                                if quality_point.check_execute_now():
                                    check_values = ml._get_check_values(quality_point)
                                    clause_check_values_list.append(check_values)
                            check_vals_list += clause_check_values_list

        self.env['quality.check'].sudo().create(check_vals_list) 
