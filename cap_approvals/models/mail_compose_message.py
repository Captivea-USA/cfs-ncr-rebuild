# -*- coding: utf-8 -*-

from odoo import models, fields, api
import lxml.etree as et


# EOI-543: Make acknowledgement buttons text white
BUTTONS_TEMPLATE = """
<div id='buttons_acknowledgement'>
    <br>
    <a href="%s/acknowledgement/acknowledged/%s/%s" class="btn btn-primary" style="color: white" target="_blank">Yes</a>
    <a href="%s/acknowledgement/denied/%s/%s" class="btn btn-primary" style="color: white" target="_blank">No</a>
</div>
"""

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    include_acknowledgement = fields.Boolean(string='Include Acknowledgement',
                                             compute='_compute_acknowledgement',
                                             inverse='_set_acknowledgement',
                                             store=False)

    #EOI 443 - Email Acknowledge
    @api.depends('template_id.include_acknowledgement')
    def _compute_acknowledgement(self):
        for rec in self:
            rec.include_acknowledgement = rec.template_id.include_acknowledgement
    
    #EOI 443 - Email Acknowledge
    def _set_acknowledgement(self):
        pass

    #EOI 443 - Email Acknowledge
    @api.onchange('include_acknowledgement', 'body')
    def _include_acknowledgement_buttons(self):
        self.ensure_one()
        if self.body:
            parser = et.HTMLParser()
            tree = et.fromstring(self.body, parser)
            if self.include_acknowledgement:
                # Add button to body if it does not have one already
                if not tree.xpath("//div[@id=\'buttons_acknowledgement\']"):
                    url_path = self.get_base_url()
                    buttons_html = BUTTONS_TEMPLATE % (url_path, self.model.replace(".","_"), str(self.res_id),
                                                       url_path, self.model.replace(".","_"), str(self.res_id))
                    button_div = et.fromstring(buttons_html, parser)
                    tree.append(button_div)
            else:
                # Remove button(s) from body if it has one
                for button_div in tree.xpath("//div[@id=\'buttons_acknowledgement\']"):
                    button_div.getparent().remove(button_div)

            self.body = et.tostring(tree, pretty_print=True, method='html')

