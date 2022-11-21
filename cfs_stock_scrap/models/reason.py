# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class cfs_stock_cmethod(models.Model):
    _name = 'stock.scrap.reason'
    _description = 'Reason for scrapping'

    name = fields.Char(string="Reason")
