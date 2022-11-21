# -*- coding: utf-8 -*-
######################################################################################
#
#    Captivea
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

{
    'name': 'CAP Purchase Approvals',
    'version': '15.0.0.2',
    'summary': 'Gives the ability to have multi stage approvals on PO and approvals for Bills',
    'description': """Adds PO states and allows user to go through the approval workflow on POs and bills
                """,
    'category': 'Accounting',
    'author': 'Captivea LLC, BEL',
    'company': 'Captivea LLC',
    'maintainer': 'https://www.captivea.com/',
    'depends': ["cfs_autoexec", 'base', 'sale', 'account', 'purchase', 'cfs_account' ,'analytic', 'account_budget', 'website', 'mail', 'multi_level_approval', 'multi_level_approval_configuration', 'account_3way_match'],
    'website': 'https://www.captivea.com/',
    'data': [
        'data/mail_template.xml',
        'views/account_analytic_account.xml',
        'views/account_move_view.xml',
        'views/crossovered_budget.xml',
        'views/mail_views.xml',
        'views/purchase_order_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/web_templates.xml',
    ],
    'qweb': [],
    'images': ['static/description/icon.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
