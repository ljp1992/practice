# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    name = fields.Char(string=u'销售单号')#唯一 系统自动生成
    customer_id = fields.Many2one('customer', string=u'客户')

