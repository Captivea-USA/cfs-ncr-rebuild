from odoo import models, api


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def default_get(self, default_fields):
        """
        EOI136
        Override default_get to include the default vendor id sent from the context
        First check if parent id is already created because this function is used frequently
        """

        values = super().default_get(default_fields)
        context = self.env.context
        if context and not values.get("parent_id"):
            values.update({"parent_id": context.get("default_vendor_id")})
        return values
