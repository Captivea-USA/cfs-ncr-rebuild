from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_default = fields.Boolean("Payment Default")

    # EOI-392: Add default Journal on Register Payment wizard
    def write(self, vals):
        if vals.get("payment_default"):
            journals = self.env["account.journal"].search([("payment_default", "!=", False)])
            if journals:
                raise ValidationError(f"Only one Journal may be set as the payment default Journal. The current payment default Journal is {journals.id}.")
        return super(AccountJournal, self).write(vals)