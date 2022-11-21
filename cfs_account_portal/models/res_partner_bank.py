# -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.base_iban.models.res_partner_bank import normalize_iban, pretty_iban, get_bban_from_iban, validate_iban, _map_iban_template

import logging

_logger = logging.getLogger(__name__)
        
class ResPartnerBank(models.Model):
    _name = 'res.partner.bank'
    _inherit = ['encryption.mixin', 'res.partner.bank']

    # Already existing fields. Adding encrypted parameter
    acc_number = fields.Char(encrypted=True)
    acc_holder_name = fields.Char(encrypted=True)

    # New fields
    aba_routing = fields.Char(string='ABA/Routing', help='American Bankers Association Routing Number', encrypted=True)
    swift = fields.Char(string='SWIFT', encrypted=True)
    account_type = fields.Selection([('c', 'Checking'), ('s', 'Savings')], string='Account Type')
    b_name = fields.Char(string='Bank Name', encrypted=True)

    def _valid_field_parameter(self, field, name):
        return name == 'encrypted' or super(ResPartnerBank, self)._valid_field_parameter(field, name)

    @api.constrains('aba_routing')
    def _check_aba_routing(self):
        for bank in self:
            if bank.aba_routing and not re.match(r'^\d{1,9}$', self._decrypt_data(bank.aba_routing)):
                raise ValidationError(_('ABA/Routing should only contains numbers (maximum 9 digits).'))

    def flabel(self,field_name):
        # Return Database Label from technical name
        field = self.env['ir.model.fields'].search([('model','=',self._name),('name','=',field_name)])
        if field:
            return field.field_description
        else:
            return field_name

    @api.model
    def retrieve_acc_type(self, acc_number):
        try:
            acc_number = self._decrypt_data(acc_number)
        except:
            pass
        try:
            validate_iban(acc_number)
            return 'iban'
        except ValidationError:
            return super(ResPartnerBank, self).retrieve_acc_type(acc_number)

    def get_bban(self):
        if self.acc_type != 'iban':
            raise UserError(_("Cannot compute the BBAN because the account number is not an IBAN."))
        return get_bban_from_iban(self.acc_number)

    # ERPPROD-128 - Remove duplicate write and create method on res_partner_bank
    # The commented out create and write methods below were removed because they
    # redundantly duplicated decryption
    # @api.model
    # def create(self, vals):
    #     if vals.get('acc_number'):
    #         try:
    #             vals['acc_number'] = self._decrypt_data(vals['acc_number'])
    #         except:
    #             pass
    #         try:
    #             validate_iban(vals['acc_number'])
    #             vals['acc_number'] = pretty_iban(normalize_iban(vals['acc_number']))
    #         except ValidationError:
    #             pass
    #     return super(ResPartnerBank, self).create(vals)

    # ERPPROD-128 - Remove duplicate write method on res_partner_bank
    # def write(self, vals):
    #     if vals.get('acc_number'):
    #         try:
    #             vals['acc_number'] = self._decrypt_data(vals['acc_number'])
    #         except:
    #             pass
    #         try:
    #             validate_iban(vals['acc_number'])
    #             vals['acc_number'] = pretty_iban(normalize_iban(vals['acc_number']))
    #         except ValidationError:
    #             pass
    #     return super(ResPartnerBank, self).write(vals)

    @api.constrains('acc_number')
    def _check_iban(self):
        for bank in self:
            if bank.acc_type == 'iban':
                acc_number = bank.acc_number
                try:
                    acc_number = self._decrypt_data(bank.acc_number)
                except:
                    pass
                validate_iban(acc_number)

    def check_iban(self, iban=''):
        try:
            iban = self._decrypt_data(iban)
        except:
            pass
        try:
            validate_iban(iban)
            return True
        except ValidationError:
            return False

    def write(self, values):
        if self.env.user.has_group('base.group_portal') and len(self)==1:

            body = "FYI: This Vendor has updated their bank information via the Vendor Portal."

            folks_to_notify = self.env.ref('purchase.group_purchase_manager')

            existing_followers = self.partner_id and self.partner_id.message_partner_ids and self.partner_id.message_partner_ids.ids

            if folks_to_notify and folks_to_notify.users:
                folks_for_this = list(set(folks_to_notify.users.partner_id.ids)-set(existing_followers))
                self.partner_id.message_subscribe(partner_ids=folks_for_this, subtype_ids=[self.env.ref('mail.mt_note').id])
                self.partner_id.message_post(body=body)
                self.partner_id.message_unsubscribe(partner_ids=folks_for_this)

        return super(ResPartnerBank, self).write(values)