# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    permission = fields.Selection(selection=[('salesman',u'业务员'),('manager',u'经理')], default='salesman', string=u'权限')
    useable = fields.Boolean(string=u'可用', default=True)