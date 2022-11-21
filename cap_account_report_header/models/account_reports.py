# -*- coding: utf-8 -*-
import datetime
import pytz
import io
from odoo.tools.misc import xlsxwriter
from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def display_headers(self, options):
        customize_header = {}
        if self and self.name in ('Profit and Loss', 'Balance Sheet') or 'model' in self._context and self._context.get('model') in ('account.cash.flow.report', 'account.general.ledger', 'account.generic.tax.report', 'account.aged.receivable', 'account.aged.payable'):
            if 'date' in options and options.get('date'):
                date_options = options.get('date')
                customize_header['period_range'] = ''
                timestamp = datetime.datetime.now()
                context_tz = pytz.timezone(self.env.user.tz)
                utc_timestamp = pytz.utc.localize(timestamp, is_dst=False)
                time_range = utc_timestamp.astimezone(context_tz).strftime("%I:%M %p")
                if date_options.get('period_type') in ('month','quarter','fiscalyear') and date_options.get('filter') in ('this_month','this_quarter','this_year'):
                    customize_header['period_range'] = 'From '+ date_options.get('date_from') + ' To ' + str(datetime.date.today())
                else:
                    customize_header['period_range'] = 'From '+ date_options.get('date_from') + ' To ' + date_options.get('date_to')
                customize_header['company'] = self.env.company.name
                customize_header['current_date_time'] = 'Run Date: '+str(datetime.date.today())+' '+ time_range
        return customize_header

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        self = self.with_context(self._set_context(options)) # For multicompany, when allowed companies are changed by options (such as aggregare_tax_unit)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        report_manager = self._get_report_manager(options)

        # Custom Code Start
        options['customize_header'] = self.display_headers(options)
        if self._get_report_name() in ('Profit and Loss', 'Balance Sheet','Cash Flow Statement', 'General Ledger', 'Tax Report', 'Aged Receivable', 'Aged Payable'):
            if 'multi_company' in options and options.get('multi_company'):
                options['customize_multi_company'] = options['multi_company']
        # Custom Code End

        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(options),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info

    def print_pdf(self, options):
        if self and self.name in ('Profit and Loss', 'Balance Sheet') or 'model' in self._context and self._context.get('model') in ('account.cash.flow.report', 'account.general.ledger', 'account.generic.tax.report', 'account.aged.receivable', 'account.aged.payable'):
            customize_header = options['customize_header']
            options['customize_header'] = {}
            if 'multi_company' in options and options.get('multi_company'):
                customize_multi_company = options['multi_company']
                options['customize_multi_company'] = customize_multi_company
                options['multi_company'] = []
            options['date']['string'] = customize_header['period_range']
            options['date']['current_date'] = customize_header['current_date_time']
        return super(AccountReport, self).print_pdf(options)

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        #Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        headers, lines = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

        #Custom Code Start
        if self._get_report_name() in ('Profit and Loss', 'Balance Sheet','Cash Flow Statement', 'General Ledger', 'Tax Report', 'Aged Receivable', 'Aged Payable'):
            customize_header = options['customize_header']
            if self._get_report_name() == 'Profit and Loss':
                headers[0].append({'name': 'Profit and Loss'})
            elif self._get_report_name() == 'Balance Sheet':
                headers[0].append({'name': 'Balance Sheet'})
            elif self._get_report_name() == 'Cash Flow Statement':
                headers[0].append({'name': 'Cash Flow Statement'})
            elif self._get_report_name() == 'General Ledger':
                headers[0].append({'name': 'General Ledger'})
            elif self._get_report_name() == 'Tax Report':
                headers[0].append({'name': 'Tax Report'})
            elif self._get_report_name() == 'Aged Receivable':
                headers[0].append({'name': 'Aged Receivable'})
            elif self._get_report_name() == 'Aged Payable':
                headers[0].append({'name': 'Aged Payable'})

            headers[0].append({'name': customize_header['period_range']})
            if 'multi_company' in options and options.get('multi_company'):
                customize_multi_company = options.get('multi_company')
                cnt = 0
                company_name = 'Companies: '
                for company in customize_multi_company:
                    if cnt == 0:
                        company_name = company_name + company.get('name')
                    if cnt > 0:
                        company_name = company_name + ' | ' + company.get('name')
                    cnt += 1

                headers[0].append({'name': company_name})
            else:
                headers[0].append({'name': customize_header['company']})
            headers[0].append({'name': customize_header['current_date_time']})

        # Add headers.
        if self._get_report_name() in ('Profit and Loss', 'Balance Sheet','Cash Flow Statement', 'General Ledger', 'Tax Report', 'Aged Receivable', 'Aged Payable'):
            for header in headers:
                x_offset = 0
                for column in header[-4:]:
                    column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                    colspan = column.get('colspan', 1)
                    if colspan == 1:
                        sheet.write(y_offset, x_offset, column_name_formated, title_style)
                    else:
                        sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated, title_style)
                    y_offset += 1
                del header[-4:]

        # Custom Code End
        for header in headers:
            x_offset = 0
            for column in header:
                column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                colspan = column.get('colspan', 1)
                if colspan == 1:
                    sheet.write(y_offset, x_offset, column_name_formated, title_style)
                else:
                    sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated, title_style)
                x_offset += colspan
            y_offset += 1

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            #write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            #write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file


class AccountGenericTaxReport(models.AbstractModel):
    _inherit = 'account.generic.tax.report'

    def _get_columns_name(self, options):
        columns_header = [{'style': 'width: 100%'}]
        if self._is_generic_layout(options):
            # Custom Code Start
            columns_header = [{'style': ''}]
            # Custom Code End
            columns_header += [{'name': '%s \n %s' % (_('NET'), self.format_date(options)), 'class': 'number'}, {'name': _('TAX'), 'class': 'number'}]
            if options.get('comparison') and options['comparison'].get('periods'):
                for p in options['comparison']['periods']:
                    columns_header += [{'name': '%s \n %s' % (_('NET'), p.get('string')), 'class': 'number'}, {'name': _('TAX'), 'class': 'number'}]
        else:
            columns_header.append({'name': '%s \n %s' % (_('Balance'), self.format_date(options)), 'class': 'number', 'style': 'white-space: pre;'})
            if options.get('comparison') and options['comparison'].get('periods'):
                for p in options['comparison']['periods']:
                    columns_header += [{'name': '%s \n %s' % (_('Balance'), p.get('string')), 'class': 'number', 'style': 'white-space: pre;'}]

        return columns_header
