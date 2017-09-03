# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerFollowRecord(models.Model):
    _name = 'customer.follow.record'
    _rec_name = 'customer_id'

    # name = fields.Char(string=u'编号')
    time = fields.Datetime(string=u'跟进时间', default=fields.Datetime.now)
    content = fields.Text(string=u'内容')
    # note = fields.Text(string=u'备注')
    customer_id = fields.Many2one('customer', string=u'客户', ondelete='cascade')
