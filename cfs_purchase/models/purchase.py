# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    previous_state = fields.Char("Previous State")

    def write(self, vals):
        """
        ITERP243 - Update previous state when writing/updating record
        """
        # Needs to be before super is called so that the values aren't changed
        for rec in self:
            current_state = rec.state
            if "state" in vals:
                rec.previous_state = (
                    current_state if current_state != "closed" else None
                )
        # do regular write method
        return super().write(vals)

    def button_reset(self):
        """
        ITERP243 - Reset PO to previous state before it was closed
        """
        state = self.state
        previous_state = self.previous_state
        if state == "closed" and previous_state:
            self.state = previous_state
            return True
        elif not previous_state:
            raise ValidationError(
                "You are trying to reset the state on a PO that has no previous state."
            )
        else:
            raise ValidationError(
                "Unable to reset a purchase order that is not closed."
            )

    def action_rfq_send(self):
        """
        EOI136
        Override release button to insert the company id and email on the mail wizard database table
        """
        res = super().action_rfq_send()
        self.ensure_one()
        # We only need the vendor id for purchase orders
        if res["context"].get("default_model") == "purchase.order":
            res["context"].update({"default_vendor_id": self.partner_id.id})
        return res
