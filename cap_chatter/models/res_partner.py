from odoo import api, fields, models

# EOI-328: Configure Model for Smart Button 'Certifications'
class Partner(models.Model):
    _inherit = 'res.partner'

    cert_ids = fields.One2many(comodel_name='res.partner.certification',inverse_name='partner_id',string='Certifications')
    cert_count = fields.Integer('Number of Certifications', compute="_compute_cert_count")

    @api.depends('cert_ids')
    def _compute_cert_count(self):
        for record in self:
            record.cert_count = len(record.cert_ids)


class Certification(models.Model):
    _name = 'res.partner.certification'
    _description = 'Vendor Certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name')
    type = fields.Many2one('res.partner.certification.type','Certification Type')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('Expiry Date')
    partner_id = fields.Many2one('res.partner','Contact')

    # EOI - 431: auto populate the partner
    partner_id = fields.Many2one('res.partner', 'Contact', default=lambda self: self.env['res.partner'].browse(self.env.context.get('search_default_partner_id')))

class CertificationType(models.Model):
    _name = 'res.partner.certification.type'
    _description = 'Vendor Certification Types'
    _order = 'name'

    name = fields.Char('Name')