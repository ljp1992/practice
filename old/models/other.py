# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Country(models.Model):
    _name = 'country'

    name = fields.Char(string=u'国家')
    note = fields.Text(string=u'备注')

class Position(models.Model):
    _name = 'position'

    name = fields.Char(string=u'职位')
    note = fields.Text(string=u'备注')