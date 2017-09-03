# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Product(models.Model):
    _name = 'product'

    name = fields.Char(string=u'产品名称')
    code = fields.Char(string=u'产品编码')
    customer_ids = fields.Many2many('customer','customer_product_rel','product_id','customer_id',string=u'客户')
