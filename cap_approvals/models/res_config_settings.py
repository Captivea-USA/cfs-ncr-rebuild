from odoo import fields, models, api, _
 
 # EOI-349: Needed for the _get_approver_vals function to work
class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    # EOI-552/559: Change Level 30s and 50s to Char fields from Integer
    cfs_purchase_order_finance_users = fields.Char(string="Finance User", config_parameter="cap_settings.cfs_purchase_order_finance_users")
    cfs_purchase_manager_users = fields.Char(string="Purchase Manager", config_parameter="cap_settings.cfs_purchase_manager_users")
    cfs_skip_purchase_manager_users = fields.Char(string="Skip Purchase Manager", config_parameter="cap_settings.cfs_skip_purchase_manager_users")
    cfs_purchase_order_ceo_id = fields.Integer(string="CEO", config_parameter="cap_settings.cfs_purchase_order_ceo_id")
    cfs_min_amount_ceo = fields.Integer(string="Minimum Amount CEO", config_parameter="cap_settings.cfs_min_amount_ceo")
    cfs_cfo = fields.Integer(string="CFO", config_parameter="cap_settings.cfs_cfo")
