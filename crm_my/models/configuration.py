# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Configuration(models.Model):
    _name = 'configuration'

    name = fields.Char(default=u'设置')
    so_jiaohuo_remind = fields.Integer(string=u'销售订单交货日期提醒')