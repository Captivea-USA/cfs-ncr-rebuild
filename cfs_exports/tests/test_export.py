
from datetime import datetime
from .common import ExportsCommon,setAssertionFunction

class TestExportReports(ExportsCommon):
    def test_export_datetime_pass(self):
        """
        Given datetime can properly be converted
        """
        setAssertionFunction("test_export_datetime_pass")
        try:
            formatted_date = self.env['export.reports']._export_datetime(date_object=datetime.now())
            datetime.strptime(formatted_date, "%B %d %Y")
            self.assertTrue(formatted_date)
        except Exception as err:
            self.assertionErrors.append(err)

    def test_export_datetime_fail(self):
        """
        Given datetime will fail given incorrect data
        """
        setAssertionFunction("test_export_datetime_fail")
        try:
            formatted_date = self.env['export.reports']._export_datetime(date_object="superman")
            datetime.strptime(formatted_date, "%B %d %Y")
            self.assertTrue(formatted_date)
        except Exception as err:
            self.assertionErrors.append(err)

    

    def test_export_many2one_pass(self):
        """
        Given many2one will pass
        """
        setAssertionFunction("test_export_many2one_pass")
        comodel = "res.users"
        res_name = "login"
        field_name = "buyer_id"
        try:
            res_partner = self.env['res.partner'].browse(4232)
            field_value = getattr(res_partner, field_name)
            field_value = (field_value.id, field_value.name)
            many2one_value = self.env['export.reports']._export_many2one(values=field_value, table_display=(comodel, res_name))
            is_string = isinstance(many2one_value, str)
            self.assertTrue(is_string)
        except Exception as err:
            self.assertionErrors.append(err)

    def test_export_many2one_fail(self):
        """
        Given many2one will fail with incorrect res_name
        """
        setAssertionFunction("test_export_many2one_fail")
        comodel = "res.users"
        res_name = "afdafdsafsa"
        field_name = "buyer_id"
        try:
            res_partner = self.env['res.partner'].browse(4232)
            field_value = getattr(res_partner, field_name)
            field_value = (field_value.id, field_value.name)
            many2one_value = self.env['export.reports']._export_many2one(values=field_value, table_display=(comodel, res_name))
            is_string = isinstance(many2one_value, str)
            self.assertTrue(is_string)
        except Exception as err:
            self.assertionErrors.append(err)