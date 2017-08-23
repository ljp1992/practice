# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    name = fields.Char(string=u'采购单号')#唯一 系统自动生成

