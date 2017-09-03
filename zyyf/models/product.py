# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Product(models.Model):
    _name = 'product'

    name = fields.Char(string=u'产品名称')
    code = fields.Char(string=u'产品编码')
    note = fields.Char(string=u'备注')
