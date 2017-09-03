# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

class Customer(models.Model):
    _name = 'customer'

    name = fields.Char(string=u'公司名称')
    address = fields.Char(string=u'地址')
    website = fields.Char(string=u'网址')
    develop_time = fields.Datetime(string=u'开发时间', default=fields.Datetime.now)
    last_contact_time = fields.Datetime(string=u'上次联系时间', default=fields.Datetime.now)
    note = fields.Text(string=u'备注')
    active = fields.Boolean(string=u'可用', default=True)
    so_qty = fields.Float(string=u'销售订单数', store=False, compute='_get_so_qty')
    del_days = fields.Integer(string=u'间隔天数', related='grade_id.del_time', store=False)
    # del_days_final = fields.Integer(string=u'最终的间隔天数', store=False)
    origin_id = fields.Many2one('customer.origin', string=u'来源')
    grade_id = fields.Many2one('customer.grade', string=u'客户等级')
    category_id = fields.Many2one('customer.category', string=u'客户类型')
    develop_person = fields.Many2one('res.users', string=u'业务员', default=lambda self: self.env.user.id)
    country_id = fields.Many2one('country', string=u'国家')
    customer_state = fields.Many2one('customer.state', string=u'状态')
    sale_orders = fields.One2many('sale.order', 'customer_id', string=u'销售订单')
    so_remind_ids = fields.One2many('sale.order.remind', 'customer_id', string=u'交货日期提醒')
    # product_ids = fields.Many2many('product','customer_product_rel','customer_id','product_id',string=u'意向产品')
    contact_ids = fields.Many2many('customer.contact.person', 'customers_contacts_rel', 'customer_id', 'contact_id',
                                   string=u'联系人')


    _sql_constraints = [
        ('CompanyName_unique', 'unique (name)', u'系统中已存在该公司！'),
        ('website_unique', 'unique (website)', u'系统中已存在该公司网址！'),
    ]



    #获取销售订单数
    @api.one
    def _get_so_qty(self):
        for record in self:
            record.so_qty = len(record.sale_orders)

    #跳转到销售订单tree视图
    @api.multi
    def view_sale_order(self):
        return {
            'name': _(u'销售订单'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
        }

    #customer contacter One2many的关系
    @api.model
    def create(self, vals):
        contact_ids = vals.get('contact_ids')
        if contact_ids and len(contact_ids) >= 1:
            for item in contact_ids:
                if len(item) == 3:
                    c_t_ps = self.env['customer.contact.person'].browse(item[2])
                    for c_t_p in c_t_ps:
                        if c_t_p.customer_ids:
                            info = u"【%s】已经是【%s】的联系人！" % (c_t_p.name, c_t_p.customer_ids.name)
                            raise ValidationError(_(info))
        return super(Customer, self).create(vals)

    # customer contacter One2many的关系
    @api.multi
    def write(self, vals):
        contact_ids = vals.get('contact_ids')
        # print self.id,self.ids
        if contact_ids and len(contact_ids) >= 1:
            for item in contact_ids:
                if len(item) == 3:
                    c_t_ps = self.env['customer.contact.person'].browse(item[2])
                    for c_t_p in c_t_ps:
                        # print c_t_p.customer_ids.id
                        if c_t_p.customer_ids and c_t_p.customer_ids.id != self.id:
                            info = u"【%s】已经是【%s】的联系人！" % (c_t_p.name, c_t_p.customer_ids.name)
                            raise ValidationError(_(info))
        #update last_contact_time
        # last_contact_time = vals.get('last_contact_time')
        # if last_contact_time:
        #     records = self.env['contact.customer'].search([('state','=','to_do'),('customer_id','=',self.id)])
        #     if records:
        #         if len(records) >= 2:
        #             info = u'有多条联系该客户的记录'
        #             raise ValidationError(_(info))
        #         elif len(records) == 1:
        #             last_contact_time = datetime.datetime.strptime(last_contact_time, '%Y-%m-%d %H:%M:%S')
        #             if last_contact_time + datetime.timedelta(days=self.del_days) > datetime.datetime.now():
        #                 records[0].state = 'done'

        return super(Customer, self).write(vals)

    #查看客户跟踪记录
    def view_customer_follow_record(self):
        # print self.id
        return {
            'name': _(u'客户跟踪记录'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer.follow.record',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('customer_id','=',self.id)],
        }

class CustomerContactPerson(models.Model):
    _name = 'customer.contact.person'

    name = fields.Char(string=u'姓名')
    position = fields.Many2one('position', string=u'职位')
    email = fields.Char(string=u'邮箱')
    phone = fields.Char(string=u'电话',default='+')
    cellphone = fields.Char(string=u'手机')
    chuanzhen = fields.Char(string=u'传真')
    skype = fields.Char(string=u'skype')
    other = fields.Char(string=u'其他联系方式')
    qq = fields.Char(string=u'QQ')
    wechat = fields.Char(string=u'WeChat')
    whatsapp = fields.Char(string=u'WhatsApp')
    note = fields.Text(string=u'备注')
    customer_ids = fields.Many2many('customer','customers_contacts_rel','contact_id','customer_id',string=u'客户')

    _sql_constraints = [
        ('Email_unique', 'unique (email)', u'该邮箱已存在！'),
        ('phone_unique', 'unique (phone)', u'该电话已存在！'),
        ('Cellphone_unique', 'unique (cellphone)', u'该手机已存在！'),
        ('Chuanzhen_unique', 'unique (chuanzhen)', u'该传真已存在！'),
        ('Skype_unique', 'unique (skype)', u'skype已存在！'),
        ('MSN_unique', 'unique (msn)', u'msn已存在！'),
        ('QQ_unique', 'unique (qq)', u'QQ已存在！'),
        ('Wechat_unique', 'unique (wechat)', u'微信已存在！'),
        ('WhatsApp_unique', 'unique (whatsapp)', u'WhatsApp已存在！'),
    ]

class CustomerOrigin(models.Model):
    _name = 'customer.origin'

    name = fields.Char(string=u'客户来源')
    note = fields.Text(string=u'备注')

class CustomerGrade(models.Model):
    _name = 'customer.grade'

    name = fields.Char(string=u'客户等级')
    del_time = fields.Integer(string=u'间隔天数',help=u'多久联系一次')
    note = fields.Text(string=u'备注')

class CustomerCategory(models.Model):
    _name = 'customer.category'

    name = fields.Char(string=u'名称')
    note = fields.Text(string=u'备注')

class CustomerState(models.Model):
    _name = 'customer.state'

    name = fields.Char(string=u'客户状态')
    note = fields.Text(string=u'备注')