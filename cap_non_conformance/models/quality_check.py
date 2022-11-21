# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    cfs_ncr_ids = fields.One2many('ncr', string='Non-Conformance Reports', inverse_name='cfs_quality_check_id',)
    cfs_ncr_count = fields.Integer('NCR Count', compute='_compute_ncr_count')

    cfs_qty_failed = fields.Integer('QTY Failed')

    def new_ncr(self):
        self.ensure_one()
        po = ""
        po_order_line = ""

        if self.picking_id:
            po = self.env['purchase.order'].search([('name', '=', self.picking_id.origin)],limit=1)

            for line in po.order_line:
                if line.product_id == self.product_id:
                    po_order_line = line
                    break
            
        ncr = self.env['ncr'].create({
            'cfs_po_num_id': po.id if po else False,
            'cfs_po_line_num_id': po_order_line.id if po_order_line else False,
            'cfs_part_value': po_order_line.price_unit if po_order_line else False,
            'cfs_supplier_id': po.partner_id.id if po else False,
            'cfs_buyer_id': po.cfs_buyer.id if po else False,
            'cfs_part_number_id': self.product_id.id,
            'cfs_quality_check_id': self.id,
            'cfs_lot_sn_id': self.lot_id.id,
            'cfs_lot_sn_name': self.lot_name if not self.lot_id else False,
            'cfs_responsible_engineer_id': self.product_id.design_owner.id,
            'cfs_qty_tested': self.qty_tested if self.qty_tested else False,
            'cfs_qty_failed': self.cfs_qty_failed,
            'cfs_type_id' : 1,
        })
        return {
            'name': ('Non-Conformance Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'ncr',
            'views': [(self.env.ref('cap_non_conformance.ncr_quality_form_view').id, 'form')],
            'res_id': ncr.id,
        }

    def action_see_ncrs(self):
        self.ensure_one()
        if len(self.cfs_ncr_ids) == 1:
            return {
                'name': ('Non-Conformance Report'),
                'type': 'ir.actions.act_window',
                'res_model': 'ncr',
                'views': [(self.env.ref('cap_non_conformance.ncr_quality_form_view').id, 'form')],
                'res_id': self.cfs_ncr_ids.ids[0],
            }
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("cap_non_conformance.ncr_quality_view")
            action['domain'] = [('id', 'in', self.cfs_ncr_ids.ids)]
            action['context'] = dict(self._context, default_check_id=self.id)
            return action

    @api.depends('cfs_ncr_ids')
    def _compute_ncr_count(self):
        for record in self:
            record.cfs_ncr_count = len(record.cfs_ncr_ids)