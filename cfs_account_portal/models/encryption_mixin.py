# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError as err:
    _logger.debug(err)


class EncryptionMixin(models.AbstractModel):
    """ Encrypts and decrypts all fields with the attribute 'encrypted' on create/write/read"""

    _name = 'encryption.mixin'
    _description = 'Field Encryption'

    def _get_cipher(self):
        # key_name = 'cfs.encryption.key'
        # key_str = self.env['ir.config_parameter'].sudo().get_param(key_name)

        key_str = tools.config['cfs_encryption_key']

        if not key_str:
            raise ValidationError(_("No '%s' entry found in system parameters.") % key_name)

        # key should be in bytes format
        key = key_str.encode()

        try:
            return Fernet(key)
        except Exception as ex:
            raise ValidationError(_('Error decrypting data: %s') % ex)

    def _is_field_encrypted(self, field_name, attribute='encrypted'):
        return bool(getattr(self._fields[field_name], attribute, False))

    @api.model
    def _encrypt_data(self, data):
        if not data:
            return False

        cipher = self._get_cipher()
        if not isinstance(data, bytes):
            data = data.encode()
        return cipher.encrypt(data or '')

    @api.model
    def _decrypt_data(self, data):
        if not data:
            return False

        cipher = self._get_cipher()
        if not isinstance(data, bytes):
            data = data.encode()
        try:
            return cipher.decrypt(data).decode()
        except InvalidToken:
            raise ValidationError(_(
                "Data has been encrypted with a different "
                "key. Unless you can recover the previous key, "
                "this data is unreadable."))

    def _get_decrypted_vals(self):
        self.ensure_one()
        vals = {}

        values_to_decrypt = {field: self[field] for field in self._fields if self._is_field_encrypted(field)}
        for field, data in values_to_decrypt.items():
            vals[field] = self._decrypt_data(data)

        return vals

    @api.model
    def create(self, values):
        if isinstance(values, dict):
            values = [values]
        for vals_dict in values:
            values_to_encrypt = {field: vals_dict[field] for field in vals_dict if self._is_field_encrypted(field)}
            for field, data in values_to_encrypt.items():
                encrypted = self._encrypt_data(data)
                if encrypted:
                    vals_dict[field] = encrypted.decode()

        res = super(EncryptionMixin, self).create(values)
        return res

    def write(self, values):
        values_to_encrypt = {field: values[field] for field in values if self._is_field_encrypted(field)}
        for field, data in values_to_encrypt.items():
            encrypted = self._encrypt_data(data)
            if encrypted:
                values[field] = encrypted.decode()

        res = super(EncryptionMixin, self).write(values)
        return res


    def read(self, fields=None, load='_classic_read'):
        res = super(EncryptionMixin, self).read(fields, load)

        for record in res:
            values_to_decrypt = {field: record[field] for field in record if self._is_field_encrypted(field)}
            for field, data in values_to_decrypt.items():
                record[field] = self._decrypt_data(data) if data else False

        return res

    def name_get(self):
        """Overwriting base name_get but taking into account fields that need to be decrypted."""

        result = []
        name = self._rec_name
        if name in self._fields:
            convert = self._fields[name].convert_to_display_name
            for record in self:
                #============= Custom Code Start ====================
                if self._is_field_encrypted(name):
                    data = self._decrypt_data(record[name])
                else:
                    data = record[name]
                #============= Custom Code End ====================

                result.append((record.id, convert(data, record)))

        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))

        return result
