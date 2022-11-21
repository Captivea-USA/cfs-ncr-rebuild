from odoo import models, api, _


class MultiApprovalLine(models.Model):
    _inherit = 'multi.approval.line'

    def create(self, vals):
        res = super(MultiApprovalLine, self).create(vals)
        # EOI-576: PO Approval Chatter for all levels
        if self._context.get('uid') != 1:
            # If user is not sudo it means it is a manual creation and we must log the change in the chatter
            for record in res:
                if record.user_ids:
                    level_descriptions = {
                      10: 'Requester Approval - Level ',
                      20: 'Design Owner (direct) Approval - Level ',
                      30: 'Finance User (no budget available) Approval - Level ',
                      40: 'Budget Owner Approval - Level ',
                      50: 'Purchase Manager (high value) Approval - Level ',
                      60: 'CEO (very high value) Approval - Level ',
                    }
                    msg = (
                        level_descriptions.get(record.level, "Custom Approval - Level ")
                        + str(record.level)
                        + " - "
                    )
                    # msg = _('Level %(level)d created - ', level=record.level)
                    for user in record.user_ids:
                        msg += user.name + ", "
                    msg = msg.strip(", ") + ". "
                    record.approval_id.message_post(body=msg)
        return res