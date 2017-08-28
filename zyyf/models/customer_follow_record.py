# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerFollowRecord(models.Model):
    _name = 'customer.follow.record'
    _rec_name = 'customer_id'

    # name = fields.Char(string=u'编号')
    date = fields.Datetime(string=u'日期', default=fields.Datetime.now)
    question = fields.Text(string=u'问题')
    solution = fields.Text(string=u'解决办法')
    note = fields.Text(string=u'备注')
    customer_id = fields.Many2one('customer', string=u'客户')
