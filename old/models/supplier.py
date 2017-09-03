# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Supplier(models.Model):
    _name = 'supplier'

    name = fields.Char(string=u'公司名称')#唯一 系统自动生成
    po_qty = fields.Float(string=u'采购订单数', store=False, compute='_get_po_qty')
    purchase_orders = fields.One2many('purchase.order', 'supplier_id', string=u'采购订单')

    @api.one
    def _get_po_qty(self):
        for record in self:
            record.po_qty = len(record.purchase_orders)

    @api.multi
    def view_purchase_order(self):
        return {
            'name': _(u'采购订单'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('supplier_id', '=', self.id)],
        }
