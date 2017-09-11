# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from lxml import etree
import json


class Customer(models.Model):
    _name = 'customer'

    name = fields.Char(string=u'客户名称')
    website = fields.Char(string=u'网址')
    develop_time = fields.Datetime(string=u'开发时间', default=fields.Datetime.now)
    last_contact_time = fields.Datetime(string=u'上次联系时间', default=fields.Datetime.now)
    next_contact_time = fields.Datetime(string=u'下次联系时间')
    address = fields.Text(string=u'详细地址')
    note = fields.Text(string=u'备注')
    image = fields.Binary("Image", attachment=True, help=u"照片不能超过1024*1024px")
    quotation_qty = fields.Float(string=u'报价单数', store=False, compute='_get_quotation_qty')
    cfr_qty = fields.Float(string=u'跟进记录数量', store=False, compute='_get_cfr_qty')
    interval_days = fields.Integer(string=u'间隔天数')
    grade_id = fields.Many2one('customer.grade', string=u'级别')
    type_id = fields.Many2one('customer.type', string=u'类型')
    origin_id = fields.Many2one('customer.origin', string=u'来源')
    customer_state = fields.Many2one('customer.state', string=u'状态')
    salesman_id = fields.Many2one('res.users', string=u'当前负责人', default=lambda self: self.env.user.id)
    develop_id = fields.Many2one('res.users', string=u'开发人', default=lambda self: self.env.user.id)
    country_id = fields.Many2one('country', string=u'国家')
    contacter_ids = fields.One2many('customer.contacter', 'customer_id', string=u'联系人')
    cfr_ids = fields.One2many('customer.follow.record', 'customer_id', string=u'客户跟进记录')
    so_ids = fields.One2many('sale.order', 'customer_id', string=u'报价单')
    label_ids = fields.Many2many('customer.label', 'customer_label_rel', 'customer_id', 'label_id', string=u'标签')
    contacter_name = fields.Char(related='contacter_ids.name', string=u'联系人姓名', store=False)
    contacter_phone = fields.Char(related='contacter_ids.phone', string=u'联系人电话', store=False)
    contacter_email = fields.Char(related='contacter_ids.email', string=u'联系人email', store=False)

    # so_remind_ids = fields.One2many('sale.order.remind', 'customer_id', string=u'交货日期提醒')
    # province_id = fields.Many2one('province', string=u'省／州')
    # city_id = fields.Many2one('city', string=u'市')
    # street_id = fields.Many2one('street', string=u'街道')
    # category_id = fields.Many2one('customer.category', u'标签')

    #设置form必填项
    def set_form_field_required(self, doc):
        required_fields = self.env['customer.configuration'].get_required_fields()
        for field in required_fields:
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                # node.set('required', '1')
                modifiers = json.loads(node.get("modifiers"))
                modifiers['required'] = True
                node.set("modifiers", json.dumps(modifiers))

    #隐藏form视图字段
    def set_form_field_invisible(self, doc):
        invisible_fields = self.env['customer.configuration'].get_form_invisible_fields()
        for field in invisible_fields:
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                modifiers = json.loads(node.get("modifiers"))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

    #隐藏tree视图字段
    def set_tree_field_invisible(self, doc):
        invisible_fields = self.env['customer.configuration'].get_tree_invisible_fields()
        for field in invisible_fields:
            print field
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                modifiers = json.loads(node.get("modifiers"))
                modifiers['tree_invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

    #设置其他情况
    def set_other_field_attr(self, doc):
        invisible_fields = self.env['customer.configuration'].get_form_invisible_fields()
        if 'develop_id' not in invisible_fields:
            if self.user_has_groups('zyyf.salesman'):  # 该权限组对该字段只有读权限
                for node in doc.xpath("//field[@name='develop_id']"):
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Customer, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        # print view_id,view_type,toolbar,submenu
        if view_type == 'form':
            self.set_form_field_required(doc)#设置form必填项
            self.set_form_field_invisible(doc)
            self.set_other_field_attr(doc)
        elif view_type == 'tree':
            # print res['arch']
            self.set_tree_field_invisible(doc)
        res['arch'] = etree.tostring(doc)
        return res

    # 计算下次联系时间
    @api.onchange('interval_days', 'last_contact_time')
    def _get_next_contact_time(self):
        for record in self:
            last_contact_time = record.last_contact_time
            if last_contact_time:
                interval_days = record.interval_days
                if interval_days <= 0:
                    record.next_contact_time = ''
                else:
                    last_contact_time = datetime.datetime.strptime(last_contact_time, '%Y-%m-%d %H:%M:%S')
                    record.next_contact_time = last_contact_time + datetime.timedelta(days=interval_days)

    # unique检查
    def check_unique(self, records):
        unique_fields = self.env['customer.configuration'].get_unique_fields()
        fields_info = self.fields_get()
        for record in records:
            for field in unique_fields:
                val = record.read([field])[0][field]
                if not val:
                    continue
                results = self.sudo().search([(field,'=',val),('id','!=',record.id)])
                if results:
                    info = u'%s-%s，系统已存在' % (fields_info.get(field).get('string'), val)
                    raise UserError(info)

    #检查其他限制条件
    def check_other_restriction(self, records):
        config = self.env['customer.configuration'].sudo().browse(1)
        for record in records:
            if config.form_contacter_required:
                if not record.contacter_ids:
                    info = u'客户-%s，联系人不能为空！' % (record.name)
                    raise UserError(info)

    @api.model
    def create(self, vals):
        # print 'create customer', vals
        result = super(Customer, self).create(vals)
        self.check_unique(result)#unique检查
        self.check_other_restriction(result)
        return result

    @api.multi
    def write(self, vals):
        # print 'write customer', vals
        result = super(Customer, self).write(vals)
        self.check_unique(self)#unique检查
        self.check_other_restriction(self)
        return result

    # 获取报价单数
    # @api.multi
    # @api.depends('so_ids')
    def _get_quotation_qty(self):
        for record in self:
            record.quotation_qty = len(record.so_ids)

    #跟踪记录数量
    def _get_cfr_qty(self):
        for record in self:
            record.cfr_qty = len(record.cfr_ids)

    # 跳转到报价单tree视图
    @api.multi
    def view_quotation(self):
        return {
            'name': _(u'报价单'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
        }

    #查看客户跟进记录
    def view_customer_follow_record(self):
        return {
            'name': _(u'客户跟进记录'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer.follow.record',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
        }


    # @api.multi
    # def unlink(self):
    #     print 'unlink customer', self
    #     result = super(Customer, self).unlink()
    #     return result




#来源
class CustomerOrigin(models.Model):
    _name = 'customer.origin'

    name = fields.Char(string=u'来源')
    note = fields.Text(string=u'备注')

#级别
class CustomerGrade(models.Model):
    _name = 'customer.grade'

    name = fields.Char(string=u'级别')
    note = fields.Text(string=u'备注')

#类型
class CustomerType(models.Model):
    _name = 'customer.type'

    name = fields.Char(string=u'类型')
    note = fields.Text(string=u'备注')

#状态／阶段
class CustomerState(models.Model):
    _name = 'customer.state'

    name = fields.Char(string=u'状态')
    note = fields.Text(string=u'备注')

#客户标签
class CustomerLabel(models.Model):
    _name = 'customer.label'

    name = fields.Char(string=u'标签名')
    content = fields.Text(string=u'内容')
    customer_ids = fields.Many2many('customer','customer_label_rel','label_id','customer_id',string=u'客户')



    # name = fields.Char(string=u'标签')
    # note = fields.Text(string=u'备注')
    # parent_id = fields.Many2one('customer.category', u'上级类别')
    # child_ids = fields.One2many('customer.category','parent_id',u'子类别')
    # useable = fields.Boolean(u'有效')

