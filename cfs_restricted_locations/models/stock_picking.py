
from odoo import models
from odoo.exceptions import UserError

class PickingInherit(models.Model):
    _inherit = "stock.picking"
    # EOI-290: Add extra validation to check if the dest_location is restricted and empty
    def button_validate(self):
        lines = super(PickingInherit,self).move_line_ids_without_package
        for line in lines:
            destination = line.location_dest_id
            if destination.cfs_restricted_location and destination.quant_ids:
                empty = True
                for quant in destination.quant_ids:
                    if quant.available_quantity > 0:
                        empty = False
                if destination.quant_ids[0].lot_id != line.lot_id and  not empty:
                    raise UserError("{} is a restricted location. The product {} and the lot serial {} is already at this location the lot/serial number has to be the same. Please select another destination location".format(destination.display_name, destination.quant_ids[0].product_id.name , destination.quant_ids[0].lot_id.name))


        res = super(PickingInherit,self).button_validate()
        return res
        