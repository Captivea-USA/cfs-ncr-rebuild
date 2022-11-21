# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        if order.custom_grant_application_id:
            res.update({
                'custom_grant_application_id': order.custom_grant_application_id.id,
                'custom_grant_lead_id': order.custom_grant_lead_id.id
            })
        return res