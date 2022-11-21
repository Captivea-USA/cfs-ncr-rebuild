from odoo import _, fields, models
from ..models.multi_approval import MultiApproval

"""
Wizard to popup dynamic confirmation dialog for user
EOI377
"""
class display_dialog_box(models.TransientModel):
    _name = "confirm.dialog"
    
    approval_id = fields.Many2one(comodel_name="multi.approval")
    text = fields.Text()
    
    def btn_yes(self):
        # Go back to the regular cancel logic but set confirm to false to not reprompt
        # must pass the approval id to get the values of the approval
        MultiApproval.action_cancel(self.approval_id, confirm=False)

display_dialog_box()