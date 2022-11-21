from .common import PurchaseTestCommon, setAssertionFunction
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class PurchaseTestCase(PurchaseTestCommon):
    def test_button_reset_pass(self):
        """
        Test that button will set to previous state when the PO is closed
        """
        setAssertionFunction("test_button_reset_pass")
        # create po
        PurchaseOrder = self.env["purchase.order"].with_context(tracking_disable=True)
        company = self.env.user.company_id
        self.env["ir.sequence"].search([("code", "=", "purchase.order"),]).write(
            {
                "use_date_range": True,
                "prefix": "PO/%(range_year)s/",
            }
        )
        vals = {
            "name": "test PO",
            "partner_id": self.partner_a.id,
            "company_id": company.id,
            "currency_id": company.currency_id.id,
            "date_order": "2019-01-01",
            "project_id": 288,
            "requester_id": 2,
            "picking_type_id": 195,
            "previous_state": "draft",
            "state": "closed",
        }
        purchase_order = PurchaseOrder.create(vals.copy())
        try:
            self.assertTrue(purchase_order.button_reset())
        except AssertionError as aex:
            self.assertionErrors.append(aex)

    def test_button_reset_fail(self):
        """
        Test that button will set to previous state when the PO is closed
        """
        setAssertionFunction("test_button_reset_fail")
        # create po

        PurchaseOrder = self.env["purchase.order"].with_context(tracking_disable=True)
        company = self.env.user.company_id
        self.env["ir.sequence"].search([("code", "=", "purchase.order"),]).write(
            {
                "use_date_range": True,
                "prefix": "PO/%(range_year)s/",
            }
        )
        vals = {
            "name": "test PO",
            "partner_id": self.partner_a.id,
            "company_id": company.id,
            "currency_id": company.currency_id.id,
            "date_order": "2019-01-01",
            "project_id": 288,
            "requester_id": 2,
            "picking_type_id": 195,
            "previous_state": "draft",
            "state": "cancel",
        }
        purchase_order = PurchaseOrder.create(vals)
        try:
            with self.assertRaises(ValidationError):
                purchase_order.button_reset()
        except AssertionError as aex:
            self.assertionErrors.append(aex)

    def test_previous_state_write_pass(self):
        """
        test that the previous state is set to its initial state of canceled
        """
        setAssertionFunction("test_previous_state_write_pass")
        # create po

        PurchaseOrder = self.env["purchase.order"].with_context(tracking_disable=True)
        company = self.env.user.company_id
        self.env["ir.sequence"].search([("code", "=", "purchase.order"),]).write(
            {
                "use_date_range": True,
                "prefix": "PO/%(range_year)s/",
            }
        )
        vals = {
            "name": "test PO",
            "partner_id": self.partner_a.id,
            "company_id": company.id,
            "currency_id": company.currency_id.id,
            "date_order": "2019-01-01",
            "project_id": 288,
            "requester_id": 2,
            "picking_type_id": 195,
            "previous_state": "draft",
            "state": "cancel",
        }
        purchase_order = PurchaseOrder.create(vals)
        purchase_order.write({"state": "revised"})
        try:
            self.assertTrue(purchase_order.previous_state == "cancel")
        except AssertionError as aex:
            self.assertionErrors.append(aex)

    def test_previous_state_write_fail(self):
        """
        Test that the previous state will be set to null if the current state written is closed
        """
        setAssertionFunction("test_previous_state_write_fail")
        self.assertionFunction = "test_previous_state_write_fail"
        # create po

        PurchaseOrder = self.env["purchase.order"].with_context(tracking_disable=True)
        company = self.env.user.company_id
        self.env["ir.sequence"].search([("code", "=", "purchase.order"),]).write(
            {
                "use_date_range": True,
                "prefix": "PO/%(range_year)s/",
            }
        )
        vals = {
            "name": "test PO",
            "partner_id": self.partner_a.id,
            "company_id": company.id,
            "currency_id": company.currency_id.id,
            "date_order": "2019-01-01",
            "project_id": 288,
            "requester_id": 2,
            "picking_type_id": 195,
            "previous_state": "draft",
            "state": "closed",
        }
        purchase_order = PurchaseOrder.create(vals)
        purchase_order.write({"state": "revised"})
        try:
            self.assertTrue(not purchase_order.previous_state)
        except AssertionError as aex:
            self.assertionErrors.append(aex)