# -*- coding: utf-8 -*-
from odoo import models, api

# EOI-382: Set Employee for new CFS Related Partner
class ResPartner(models.Model):
    _inherit = "res.partner"

    # EOI-382: Set Employee for new CFS Related Partner
    @api.model_create_multi
    def create(self, partners):
        for partner in partners:
            if partner.get("email") and "@cfs.energy" in partner.get("email"):
                partner["employee"] = True
        return super(ResPartner, self).create(partners)