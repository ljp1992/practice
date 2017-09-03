# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    name = fields.Char(string=u'单号')#唯一 系统自动生成
    customer_id = fields.Many2one('customer', string=u'客户')
    confirm_date = fields.Datetime(string=u'确认日期', default=fields.Datetime.now)
    jiaohuo_date = fields.Datetime(string=u'交货日期', default=fields.Datetime.now)
    state = fields.Selection(selection=[('draft',u'草稿'),
                                        ('confirmed', u'确认'),
                                        ('done', u'完成'),], default='draft', string=u'状态')
    order_line = fields.One2many('sale.order.line', 'order_id', string=u'订单明细')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.code') or '/'
        return super(SaleOrder, self).create(vals)

    @api.one
    def confirm_order(self):
        for record in self:
            record .state = 'confirmed'

    @api.one
    def back_order(self):
        for record in self:
            record.state = 'draft'

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    order_id = fields.Many2one('sale.order', ondelete="cascade", string=u'单号')
    product_id = fields.Many2one('product', string=u'产品')
    price_unit = fields.Float(string=u'单价')
    qty = fields.Float(string=u'数量')
    subtotal = fields.Float(string=u'小计', compute='_get_subtotal', store=False)

    @api.multi
    @api.depends('price_unit','qty')
    def _get_subtotal(self):
        for record in self:
            record.subtotal = record.price_unit * record.qty


