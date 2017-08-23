# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Supplier(models.Model):
    _name = 'supplier'

    name = fields.Char(string=u'供应商编号')#唯一 系统自动生成

