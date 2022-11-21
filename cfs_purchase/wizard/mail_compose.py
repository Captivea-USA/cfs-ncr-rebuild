from odoo import models, fields


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    vendor_id = fields.Many2one(
        comodel_name="res.partner", string="Vendor ID", ondelete="set null", index=True
    )
