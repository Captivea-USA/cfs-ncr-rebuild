from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_route_process(self, message, message_dict, routes):
        """
        ERPPROD195
        override _message_route_process to remove thread id for email replies to ap@cfs.energy
        """
        local_context = {}
        for i, row in enumerate(routes) or ():
            model, thread_id, custom_values, user_id, alias = row
            if model == "account.move":
                # if the email is routed to account.move, also pass this in context
                local_context["mail_model_type"] = "account.move"
                # if a vendor bill arrives with a thread id
                if thread_id:
                    original_bill = self.env["account.move"].search(
                        [("id", "=", thread_id)], limit=1
                    )
                    if original_bill:
                        journal_name = (
                            original_bill.journal_id.name
                            if original_bill.journal_id
                            else None
                        )
                        company_name = (
                            original_bill.company_id.name
                            if original_bill.company_id
                            else None
                        )
                    else:
                        journal_name = "Vendor Bills"
                        company_name = "Commonwealth Fusion Systems LLC"
                        _logger.info(
                            f"No vendor bill found for id {thread_id}. Defaulting to company {company_name} and journal {journal_name}."
                        )
                    journal = self.env["account.journal"].search(
                        [("name", "=", journal_name), ("alias_id", "!=", False)],
                        limit=1,
                    )
                    company = self.env["res.company"].search(
                        [("name", "=", company_name)], limit=1
                    )
                    if company:
                        company_id = company.id
                    else:
                        company_id = 1
                        _logger.info(
                            f"No company id found for {company_name}. Defaulting to 1."
                        )
                    if journal:
                        journal_id = journal.id
                    else:
                        journal_id = 2
                        _logger.info(
                            f"No journal id found for {journal_name} with alias id. Defaulting to 2."
                        )
                    # remove the thread id and edit the custom values
                    thread_id = 0
                    custom_values = {
                        "move_type": "in_invoice",
                        "company_id": company_id,
                        "journal_id": journal_id,
                    }
            # redefine row with new values
            row = model, thread_id, custom_values, user_id, alias
            routes[i] = row
        # call super with any context that we've passed
        return super(
            MailThread, self.with_context(local_context)
        )._message_route_process(message, message_dict, routes)

    def message_post(self, **kwargs):
        """
        ERPPROD204 - vendor creation from email should be an internal note
        Post message to chatter
        :param: **kwargs all keyword arguments passed from previous calls. See message_post in mail_thread module for list
        """
        # subtype 2 will set this to an internal note
        # if account.type is passed in context (see _message_route_process), we want the creation chatter to be a note
        if self._context.get("mail_model_type") == "account.move":
            subtype_name = "Note"
            subtype = self.env["mail.message.subtype"].search(
                [("name", "=", subtype_name)], limit=1
            )
            if subtype:
                subtype_id = subtype.id
            elif not subtype or not subtype_id:
                subtype_id = 2
                _logger.info(
                    f"No subtype id found for {subtype_name}. Defaulting to 2."
                )
            kwargs["subtype_id"] = subtype_id
        return super().message_post(**kwargs)
