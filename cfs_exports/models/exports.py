from xmlrpc.client import Boolean
from odoo import fields, models, tools, _
import logging
import operator
import csv

# todo search the default functionality of odoo for exports
# todo can search in the logs when an export is run

# import pandas as pd

_logger = logging.getLogger(__name__)


class ExportReports(models.Model):

    _name = "export.reports"
    _description = "Export Reports"

    name = fields.Char("Name")
    directory = fields.Char("Directory")
    res_model = fields.Char("Model")
    res_model_domain = fields.Char("Model Domain")
    search_method = fields.Selection(
        [("orm", "ORM"), ("sql", "SQL")], string="Search Method"
    )

    def _export_many2one(self, values, index=1, table_display=None):
        """
        format a many2one field for export
        :param: values (tuple) - tuple of values returned from recordset
        :param: index (int) - numbered index to get from the tuple
        :param: table_display (tuple) - first index is the table name, second index is the field to get from the table
            index parameter is ignored if this parameter is specified

        :return: value - the display value for the many2one field or the tuple if index cannot be found
        """
        # if the original values is false, do not waste resources to do any logic
        if not values:
            return False
        val = values
        # if a tuple is specified and all values are filled in
        if table_display and all(table_display):
            # if the tuple cannot be parsed or the id cannot be resolved
            try:
                table = self.env[str(table_display[0])]
                field_name = str(table_display[1])
            except Exception as ex:
                _logger.error(
                    f"A table_display tuple was defined for an export but the tuple {table_display} was malformed and did not resolve a table. Error: {ex}"
                )
                return val
            try:
                record = table.browse(values[0])
            except Exception as ex:
                _logger.error(
                    f"No record could be found on {table} for id {values[0]}. Error: {ex}"
                )
                return val
            try:
                return record[field_name]
            except Exception as ex:
                _logger.error(
                    f"Field {field_name} could not be found on the record {record}. Error: {ex}"
                )
                return val
        # if the tuple table_display is not specified, return the index for the display name
        elif len(values) >= 1:
            val = values[index]
        return val

    def _export_datetime(self, date_object, format_string="%B %d %Y"):
        """
        format a datetime object for export
        :param: date_object (datetime) - object to be formatted
        :param: format_string (string) - valid string to format datetime object as string. Default: {month name} {day} {year}

        :return: val (string) - formatted string from datetime or original object if this cannot be formatted
        """
        try:
            val = date_object.strftime(format_string)
        except Exception as ex:
            _logger.error(
                f"Unable to format datetime {date_object}. Is this a valid datetime object? Error: {ex}"
            )
            return date_object
        return val

    def _export_many2many(self, values, table_name, field_name="name"):
        """
        format many2many for export

        :param: values (list)
        :param: table_name (string) - table name to search the value on the field
        :param: field_name (string) - string name of the field on the connected table with the display value
            default: name
        :return: val - comma seperated list of display values
        """
        # if values is an empty list, there is nothing to do. return an empty string
        if not values:
            return ""
        val = ""
        record_set = self.env[table_name].search([("id", "in", values)])
        for record in record_set:
            val += f"{record[field_name]}, "
        return val

    def _export_currency(self, num):
        """
        format number or float as currency

        :param: num (int/float) - input

        :return: val (string) - if num is of proper type, return a string of USD currency
        """
        if isinstance(num, (int, float)):
            return "${:,.2f}".format(num)
        return num

    def _export_string_num(self, num):
        """
        format number as string
        mainly used so that 0s aren't seen as None types

        :param: num (int/float) - value to convert to string

        :return: val (string) - string value of input
        """
        if isinstance(num, (int, float)):
            return str(num)
        return num

    def _export_string_bool(self, value):
        """
        format boolean as string
        mainly used so that 0s aren't seen as None types

        :param: value (boolean) - value to convert to string

        :return: val (string) - string value of input
        """
        if isinstance(value, bool):
            return str(value)
        return value

    def _export_selection(self, field_name, value, res_model):
        """
        format selection as the display value

        :param: field_name (string) - selection field name
        :param: value (string) - the value given by the recordset retrieved
        :param res_model (string) - name of the table to get the selection field from

        :return: val (string) - display of selection field
        """

        table = self.env.get(res_model)
        # test for type of none. truthy false evaluates an empty table as none which we do not want
        if isinstance(table, type(None)):
            _logger.error(f"No table found for {res_model}")
            return value
        selection_dict = dict(
            table.fields_get(allfields=[field_name])[field_name]["selection"]
        )
        return _(selection_dict.get(value, ""))

    def _export_compute(self, field_value, compute_function, model_name, record):
        """
        Format a computed value that needs to be reformatted
        todo function needs to be scaled and optimized but we only have two values to worry about
        
        :param: field_value (string) - value retreived from the database to be used as initial value
        :param: compute_function (string) - compute function that will be used to recreate the value
        :param: model_name (string) - the model that will contain the compute function
        :param: record (dict) - record of values returned

        :return: field_value (string) - the recreated value
        """
        model = self.env[model_name]
        if compute_function == '_compute_self_approved':
            override_id=record.get("request_owner_id")[0]
            rec = model.search([('id', '=', record["id"])])
            try:
                rec._compute_self_approved(override_id)
                field_value = rec.self_approved
            except Exception as ex:
                _logger.warning(f'Unable to recompute value {field_value} on {model_name}. Exception: {ex}')
        elif compute_function == '_compute_self_approved_timestamp':
            override_id=record.get("request_owner_id")[0]
            rec = model.search([('id', '=', record["id"])])
            try:
                rec._compute_self_approved_timestamp(override_id)
                field_value = rec.self_approved_timestamp
            except Exception as ex:
                _logger.warning(f'Unable to recompute value {field_value} on {model_name}. Exception: {ex}')
        return field_value

    def _determine_field_type(self, field_dict, record, res_model):
        """
        Use correct export function based on field type

        :param: field_dict (dict)
            todo write form
        :param: record (dict) - record from recordset as dict
        :param: res_model (string) - the local model for the data
            todo I cannot use self.res_model for some reason

        :return: val (string) - converted value based on field type
        """
        field_name = field_dict.get("name")
        field_type = field_dict.get("type")
        field_computed = field_dict.get('computed')
        field_value = record.get(field_name)
        compute_function = field_dict.get('compute_function')
        # if no type is specified, return the value without using an export function
        if not field_type:
            return field_value
        val = ""
        if field_name:
            # if the field is computed, we need to recompute it
            if field_computed:
                field_value = self._export_compute(field_value, compute_function, res_model, record)
            if field_type == "many2one":
                val = self._export_many2one(
                    values=field_value,
                    table_display=(
                        field_dict.get("comodel"),
                        field_dict.get("res_name"),
                    ),
                )
            elif field_type == "datetime":
                if type(field_value) != Boolean:
                    val = self._export_datetime(field_value)
            elif field_type == "currency":
                val = self._export_currency(field_value)
            if field_type == "selection":
                val = self._export_selection(
                    field_name=field_name,
                    value=field_value,
                    # if the comodel is not defined, we will use the local model
                    res_model=field_dict.get("comodel") or res_model,
                )
            if field_type == "string_number":
                val = self._export_string_num(field_value)
            elif field_type == "string_boolean":
                val = self._export_string_bool(field_value)
            elif field_type == "many2many":
                val = self._export_many2many(
                    values=field_value,
                    table_name=field_dict.get("comodel"),
                    field_name=field_dict.get("res_name") or "name",
                )
        return val

    def export_report(
        self, model_name, field_values, model_domain=[], search_method="orm"
    ):
        """
        export all of the purchase orders to an excel file
        ERPPROD237

        :param: model_name (string) - model to search
        :param: fields (list) - dictionaries of the fields to choose in the following form. name and label are required.
            {
                name (string) - technical name of field
                label (string) - display name of the field shown on the UI
                type (string) - type of field if any. If no type is given, the value is passed to export as it
                    type can be one of the following:
                        many2one
                        currency
                        selection
                        string_number
                        string_boolean
                        many2many
                related (bool) - If true, the comodel is used
                comodel (string) - If many2many or related is specified, this value will be used to determine the export
            }
        :param: model_domain (string) - domain to search on the model when finding records. default: []
        :param: search_metho (string) - method to search database. SQL may be faster if the fields are simple.
            ORM may be faster if the values are complicated such as computed fields.
            default: orm
            possible values:
                orm
                sql
        """
        export_directory = tools.config.get("export_directory") or self.env[
            "ir.config_parameter"
        ].sudo().get_param("export.directory")
        # if the export directory does not end with a trailing slash, append one
        if not export_directory.endswith("/"):
            export_directory += "/"
        export_file = f"{model_name}.csv"
        file_name = f"{export_directory}{export_file}"
        export_lines = []
        if search_method == "sql":
            # todo figure out how to do with raw sql
            # cursor = self.env.cr
            # if cursor:
            # query = """
            # SELECT
            #     order_id,
            #     create_date,
            #     requester_id,
            #     buyer_id,
            #     date_order,
            #     date_planned,
            #     date_promised,
            #     release_date,
            #     partner_id,
            #     product_id,
            #     vendor_part,
            #     free_description,
            #     quality_codes,
            #     buyer_category_id,
            #     override_account_id,
            #     product_qty,
            #     product_uom,
            #     price_unit,
            #     qty_received,
            #     price_subtotal,
            #     state,
            #     po_deliver_to
            # FROM
            #     purchase_order_line
            # """
            #     cursor.execute(query)
            #     purchase_order_lines = cursor.fetchall()
            pass
        else:
            # if the search method isn't recognized, default to orm
            if search_method != "orm":
                _logger.error(
                    f"Search Method {search_method} unrecognized. Defaulting to ORM"
                )
                search_method = "orm"
            records = (
                self.env[model_name]
                .search(model_domain)
                .read(
                    [
                        operator.itemgetter("name")(field_value)
                        for field_value in field_values
                    ]
                )
            )
        # format returned recordset as list of dict
        for record in records:
            export_dict = {}
            for field_value in field_values:
                converted_value = self._determine_field_type(
                    field_value, record, res_model=model_name
                )
                export_dict.update({field_value.get("label"): converted_value})

            export_lines.append(export_dict)
        # remove all false values from export
        # write to export
        with open(file_name, "w+") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    operator.itemgetter("label")(field_value)
                    for field_value in field_values
                ],
            )
            writer.writeheader()
            for line in export_lines:
                # replace values
                for key,value in line.items():
                    # erpprod255 - if the value contains a new line, replace with empty space
                    if isinstance(value, str) and '\n' in value:
                        value = value.replace('\n', ' ')
                    line[key] = '' if not value else value
                writer.writerow(line)
        # export to excel   
        self.create(
            vals_list={
                "name": export_file,
                "directory": export_directory,
                "res_model": model_name,
                "res_model_domain": model_domain,
                "search_method": search_method,
            }
        )
        return file_name