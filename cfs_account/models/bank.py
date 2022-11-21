from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    # inherit encryption to decrypt data
    _inherit = [
        "res.partner.bank",
        "mail.activity.mixin",
        "mail.thread"
    ]
    _name = "res.partner.bank"

    acc_number_mask = fields.Char(string="Account Number", compute="_mask_account")

    def _mask_account(self):
        """ERPPROD7 - Mask account number
        TODO: the original function from psus used the encryption mixin from odoo
        """
        for rec in self:
            try:
                acc_number = self._decrypt_data(rec.acc_number)
                string_number = str(acc_number)
                if len(string_number) < 4:
                    raise ValidationError(
                        "Unable to mask because the length of the account number is less than four characters"
                    )
                masked_number = "*" * (len(string_number) - 4) + string_number[-4:]
                rec.acc_number_mask = masked_number
            except Exception as ex:
                raise ValidationError(f"Unable to mask account number. Error: {ex}")

    def _email_notify(self, type="create", record=None):
        """
        ERPPROD7 - Send email notification on create/edit of records
        """
        if not record:
            raise ValidationError(
                f"No record has been specified to send the email. Please contact the administrator"
            )
        bank_id = record.id
        vendor_name = record.partner_id.name
        # form url
        base_url_param = "web.base.url"
        try:
            # sudo is need to escalate for a param
            base_url = self.env["ir.config_parameter"].sudo().get_param(base_url_param)
        except ValueError as vax:
            raise ValidationError(
                f"The system parameter {base_url_param} is not found. Please contact the administrator. Error: {vax}"
            )

        # get email template
        viewer_group = "cfs_bank_accountant_viewer"
        account_module = "cfs_account"
        template_id = "cfs_bank_account_verification_email"
        try:
            template = self.env.ref(f"{account_module}.{template_id}")
        except ValueError as vax:
            raise ValidationError(
                f"The template id {template_id} is not found in the module {account_module}. Error: {vax}"
            )

        # create email
        group = self.env.ref(f"{account_module}.{viewer_group}")
        if group:
            group_users = [user.login for user in group.users]
            email_to = ", ".join(group_users)
        else:
            email_to = ""
        email_body_header = (
            f"Vendor {vendor_name} has had a bank account updated."
            if type == "edit"
            else f"Vendor {vendor_name} has had a bank account created."
        )
        email_subject = (
            f"Updated bank account for vendor {vendor_name}"
            if type == "edit"
            else f"Create bank account for vendor {vendor_name}"
        )
        email_link = f"{base_url}/web#id={bank_id}&view_type=form&model={self._name}"
        mail_template = self.env["mail.template"].browse(template.id)
        local_context = {
            "email_to": email_to,
            "subject": email_subject,
            "email_body_header": email_body_header,
            "email_link": email_link,
        }
        # send email
        mail_template.with_context(local_context).send_mail(bank_id, force_send=True)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self._email_notify(type="create", record=res)
        return res

    def write(self, vals):
        for rec in self:
            res = super().write(vals)
            self._email_notify(type="edit", record=rec)
        return res
