from odoo.tests.common import SavepointCase


class PurchaseTestCommon(SavepointCase):
    assertionFunction = "No test provided"

    @classmethod
    def setUpClass(cls):
        """
        Setup products/account for making purchase orders
        """
        
        super().setUpClass()
        print(f'{bcolors.BOLD}CFS Purchase{bcolors.ENDC}')
        cls.assertionErrors = []
        chart_template = cls.env.ref(
            "l10n_generic_coa.configurable_chart_template", raise_if_not_found=False
        )

        cls.company_data = cls.setup_company_data(
            "company_1_data", chart_template=chart_template
        )

        cls.pay_terms_a = cls.env.ref("account.account_payment_term_immediate")
        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "partner_a",
                "property_payment_term_id": cls.pay_terms_a.id,
                "property_supplier_payment_term_id": cls.pay_terms_a.id,
                "property_account_receivable_id": cls.company_data[
                    "default_account_receivable"
                ].id,
                "property_account_payable_id": cls.company_data[
                    "default_account_payable"
                ].id,
                "company_id": False,
            }
        )
        cls.tax_sale_a = cls.company_data["default_tax_sale"]
        cls.tax_purchase_a = cls.company_data["default_tax_purchase"]

        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 800.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "taxes_id": [(6, 0, cls.tax_sale_a.ids)],
                "supplier_taxes_id": [(6, 0, cls.tax_purchase_a.ids)],
            }
        )

    def setAssertionFunction(cls, value):
        """
        Set string variable
        """
        print("running")
        cls.assertionFunction = value

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        """Create a new company having the name passed as parameter.
        Create company data
        :param chart_template: The chart template to be used on this new company.
        :param company_name: The name of the company.
        :return: A dictionary will be returned containing all relevant accounting data for testing.
        """

        def search_account(company, chart_template, field_name, domain):
            template_code = chart_template[field_name].code
            domain = [("company_id", "=", company.id)] + domain

            account = None
            if template_code:
                account = cls.env["account.account"].search(
                    domain + [("code", "=like", template_code + "%")], limit=1
                )

            if not account:
                account = cls.env["account.account"].search(domain, limit=1)
            return account

        chart_template = chart_template or cls.env.company.chart_template_id
        company = cls.env["res.company"].create(
            {
                "name": company_name,
                **kwargs,
            }
        )
        cls.env.user.company_ids |= company

        chart_template.try_loading(company=company)

        # The currency could be different after the installation of the chart template.
        if kwargs.get("currency_id"):
            company.write({"currency_id": kwargs["currency_id"]})

        return {
            "company": company,
            "currency": company.currency_id,
            "default_account_revenue": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_revenue").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_expense": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_expenses").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_receivable": search_account(
                company,
                chart_template,
                "property_account_receivable_id",
                [("user_type_id.type", "=", "receivable")],
            ),
            "default_account_payable": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    ("user_type_id.type", "=", "payable"),
                ],
                limit=1,
            ),
            "default_account_assets": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_current_assets").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_tax_sale": company.account_sale_tax_id.mapped(
                "invoice_repartition_line_ids.account_id"
            ),
            "default_account_tax_purchase": company.account_purchase_tax_id.mapped(
                "invoice_repartition_line_ids.account_id"
            ),
            "default_journal_misc": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "general")], limit=1
            ),
            "default_journal_sale": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "sale")], limit=1
            ),
            "default_journal_purchase": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "purchase")], limit=1
            ),
            "default_journal_bank": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
            ),
            "default_journal_cash": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "cash")], limit=1
            ),
            "default_tax_sale": company.account_sale_tax_id,
            "default_tax_purchase": company.account_purchase_tax_id,
        }

    @classmethod
    def tearDown(cls):
        # print any errors and then reset the assertion list
        if not cls.assertionErrors:
            print(f"{bcolors.OKBLUE}✓ Pass: {cls.assertionFunction}{bcolors.ENDC}")
        else:
            for error in cls.assertionErrors:
                print(
                    f"{bcolors.FAIL}X Fail: {cls.assertionFunction}: {error}{bcolors.ENDC}"
                )
        cls.assertionErrors = []
        # cls.assertionFunction = ""


def setAssertionFunction(value):
    PurchaseTestCommon.assertionFunction = value


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"