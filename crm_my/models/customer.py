# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class Customer(models.Model):
    _name = 'customer'

    name = fields.Char(string=u'公司名称')
    address = fields.Char(string=u'地址')
    website = fields.Char(string=u'网址')
    develop_time = fields.Datetime(string=u'开发时间', default=fields.Datetime.now)
    last_contact_time = fields.Datetime(string=u'上次联系时间')
    note = fields.Text(string=u'备注')
    origin_id = fields.Many2one('customer.origin', string=u'来源')
    grade_id = fields.Many2one('customer.grade', string=u'客户等级')
    category_id = fields.Many2one('customer.category', string=u'客户类型')
    country_id = fields.Many2one('country', string=u'国家')
    contact_ids = fields.Many2many('customer.contact.person','customers_contacts_rel','customer_id','contact_id',
                                   string=u'联系人')
    product_ids = fields.Many2many('product','customer_product_rel','customer_id','product_id',string=u'意向产品')

    _sql_constraints = [
        ('CompanyName_unique', 'unique (name)', u'系统中已存在该公司！'),
        ('website_unique', 'unique (website)', u'系统中已存在该公司网址！'),
    ]

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
        return super(Customer, self).write(vals)

    def view_customer_follow_record(self):
        print self.id
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
    phone = fields.Char(string=u'电话')
    cellphone = fields.Char(string=u'手机')
    chuanzhen = fields.Char(string=u'传真')
    skype = fields.Char(string=u'skype')
    msn = fields.Char(string=u'MSN')
    qq = fields.Char(string=u'QQ')
    wechat = fields.Char(string=u'微信')
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

    name = fields.Char(string=u'客户类型')
    note = fields.Text(string=u'备注')