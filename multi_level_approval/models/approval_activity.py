from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def activity_format(self):
        result = super(MailActivity, self).activity_format()
        activity_type_approval_id = self.env.ref(
            "approvals.mail_activity_data_approval"
        ).id
        for activity in result:
            if (
                activity["activity_type_id"][0] == activity_type_approval_id
                and activity["res_model"] == "approval.request"
            ):
                request = self.env["approval.request"].browse(activity["res_id"])
                user = self.env["res.users"].browse(activity["user_id"][0])
                approvers = request.approver_ids.filtered(
                    lambda approver: user in approver.user_ids
                )
                for approver in approvers:
                    activity["approver_id"] = approver.id
                    activity["approver_status"] = request.sudo()._compute_user_status(
                        user
                    )
        return result
