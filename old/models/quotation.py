# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Quotation(models.Model):
    _name = 'quotation'

    name = fields.Char(string=u'单号')
    note = fields.Text(string=u'备注')
    state = fields.Selection(selection=[('draft',u'草稿'),('sent',u'已发送给客户')], string=u'状态')
