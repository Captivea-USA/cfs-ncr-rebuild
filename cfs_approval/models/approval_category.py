from odoo import models, fields


class ApprovalCategory(models.Model):

    _inherit = "approval.category"

    show = fields.Boolean("Show on Approvals", default=True)

    # EOI-411: Fix approval menus and views
    def create_request(self):
        res = super(ApprovalCategory, self).create_request()
        res["context"]["hide_approval_request_id"] = True
        return res