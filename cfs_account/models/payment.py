from odoo import fields, models, api
import json
import base64
import math


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # EOI-388: Add remittance emails
    vendor_credit_ids = fields.Many2many(
        comodel_name="account.move",
        compute="_compute_vendor_credits",
        store=True,
        readonly=False,
    )

    @api.depends("reconciled_bill_ids")
    def _compute_vendor_credits(self):
        # EOI-388: Add remittance emails
        for bill in self.reconciled_bill_ids:
            self.vendor_credit_ids = None
            # Test that the widget exists and that we can get the proper data from the widget
            str_widget = bill.invoice_payments_widget
            if str_widget and "move_id" in str_widget:
                # Parse the json of the widget so that we can get the bill id
                widget = json.loads(str_widget)
                move_ids = [content.get("move_id") for content in widget["content"]]
                for move_id in move_ids:
                    # Since we only have the id number, we need to search for the record
                    account_move = self.env["account.move"].search(
                        [("id", "=", move_id)], limit=1
                    )
                    move_type = account_move.move_type
                    if move_type and move_type == "in_refund":
                        self.vendor_credit_ids += account_move

                        self.vendor_credit_ids += account_move


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    def _generate_nacha_entry_detail(self, payment):
        bank = payment.partner_bank_id
        # EOI-712: Customized to decrypt data for ABA Routing
        aba_routing = bank._decrypt_data(bank.aba_routing)
        # EOI-748: Customized to decrypt data for Account Number
        acc_number = bank._decrypt_data(bank.acc_number)
        entry = []
        entry.append("6")  # Record Type Code (PPD)
        entry.append("22")  # Transaction Code
        entry.append("{:8.8}".format(aba_routing[:-1]))  # RDFI Routing Transit Number
        entry.append("{:1.1}".format(aba_routing[-1]))  # Check Digit
        entry.append("{:17.17}".format(acc_number))  # DFI Account Number
        entry.append("{:010d}".format(round(payment.amount * 100)))  # Amount
        entry.append("{:15.15}".format(payment.partner_id.vat or ""))  # Individual Identification Number (optional)
        entry.append("{:22.22}".format(payment.partner_id.name))  # Individual Name
        entry.append("  ")  # Discretionary Data Field
        entry.append("0")  # Addenda Record Indicator

        # trace number
        entry.append("{:8.8}".format(self.journal_id.nacha_origination_dfi_identification))  # Trace Number (80-87)
        entry.append("{:07d}".format(0))  # Trace Number (88-94)

        return "".join(entry)

    def _generate_nacha_batch_control_record(self, payment, batch_nr):
        bank = payment.partner_bank_id
        # EOI-712: Customized to decrypt data for ABA Routing
        aba_routing = bank._decrypt_data(bank.aba_routing)
        control = []
        control.append("8")  # Record Type Code
        control.append("220")  # Service Class Code (credits only)
        control.append("{:06d}".format(1))  # Entry/Addenda Count
        control.append("{:010d}".format(self._calculate_aba_hash(aba_routing)))  # Entry Hash
        control.append("{:012d}".format(0))  # Total Debit Entry Dollar Amount in Batch
        control.append("{:012d}".format(round(payment.amount * 100)))  # Total Credit Entry Dollar Amount in Batch
        control.append("{:0>10.10}".format(self.journal_id.nacha_company_identification))  # Company Identification
        control.append("{:19.19}".format(""))  # Message Authentication Code (leave blank)
        control.append("{:6.6}".format(""))  # Reserved (leave blank)
        control.append("{:8.8}".format(self.journal_id.nacha_origination_dfi_identification))  # Originating DFI Identification
        control.append("{:07d}".format(batch_nr))  # Batch Number

        return "".join(control)

    def _generate_nacha_file_control_record(self, payments):
        control = []
        control.append("9")  # Record Type Code
        control.append("{:06d}".format(len(payments)))  # Batch Count

        # Records / Blocking Factor (always 10).
        # We ceil because we'll pad the file with 999's until a multiple of 10.
        block_count = math.ceil(self._get_nr_of_records(payments) / self._get_blocking_factor())
        control.append("{:06d}".format(block_count))

        control.append("{:08d}".format(len(payments)))  # Entry/ Addenda Count
        # EOI-712: Customized to decrypt data for ABA Routing
        hashes = sum(self._calculate_aba_hash(payment.partner_bank_id._decrypt_data(payment.partner_bank_id.aba_routing)) for payment in payments)
        hashes = str(hashes)[-10:] # take the rightmost 10 characters
        control.append("{:0>10}".format(hashes))  # Entry Hash

        control.append("{:012d}".format(0))  # Total Debit Entry Dollar Amount in File
        control.append("{:012d}".format(sum(round(payment.amount * 100) for payment in payments)))  # Total Credit Entry Dollar Amount in File
        control.append("{:39.39}".format(""))  # Blank

        return "".join(control)
