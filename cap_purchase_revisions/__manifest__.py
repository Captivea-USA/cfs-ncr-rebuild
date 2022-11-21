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
    'name': 'CAP PO Revisions',
    'version': '15.0.0.1',
    'summary': 'Gives the ability to create purchase order revisions',
    'description': """Business Requirements (PRO-044) - When a Purchase Order releases with revisions, it should only contain the newest revision. This is handled by editing the attached email template.
                """,
    'category': 'Purchase',
    'author': 'Captivea LLC, BEL',
    'company': 'Captivea LLC',
    'maintainer': 'https://www.captivea.com/',    
    'depends': [
        'cfs_autoexec',
        'base',
        'purchase',
        'cap_approvals',
        'cap_purchase_approval',
        'purchase_request',
        'multi_level_approval',
        ],
    'website': 'https://www.captivea.com/',
    'data': [
        'views/purchase_order_view.xml'
    ],
    'qweb': [],
    'images': ['static/description/icon.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
