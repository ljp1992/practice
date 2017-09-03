# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from lxml import etree
import json


class Customer(models.Model):
    _name = 'customer'

    name = fields.Char(string=u'名称')
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

    def cs(self, **kwargs):
        print 1111111,kwargs

    #根据权限组设置字段 是否显示 是否只读
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Customer, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self.user_has_groups('zyyf.salesman'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='develop_id']"):
                node.set('readonly', '1')
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
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

    #根据配置，校验客户是否合法 如：客户名称、网址唯一
    def check_customer_legal(self, records):
        config = self.env['configuration'].sudo().browse(1)
        for record in records:
            if config.customer_name_unique and record.name:#客户名称唯一
                results = self.sudo().search([('name','=',record.name),('id','!=',record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在客户名称——%s，该客户当前负责人为——%s' % (results[0].name, results[0].salesman_id.name)
                    raise ValidationError(_(info))
            if config.customer_website_unique and record.website:#网址唯一
                results = self.sudo().search([('website', '=', record.website), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在网址——%s，该网址所属客户为——%s，该客户当前负责人为——%s' % \
                           (results[0].website, results[0].name, results[0].salesman_id.name)
                    raise ValidationError(_(info))

    @api.model
    def create(self, vals):
        # print 'create customer', vals
        result = super(Customer, self).create(vals)
        self.check_customer_legal(result)
        return result

    @api.multi
    def write(self, vals):
        # print 'write customer', vals
        result = super(Customer, self).write(vals)
        self.check_customer_legal(self)
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

    #点击删除图标时 不删除联系人 只是customer_id置为False
    # def delete_contacter(self, vals):
    #     if vals.get('contacter_ids'):
    #         del_contacter_ids = []
    #         i = 0
    #         while True:
    #             if i >= len(vals.get('contacter_ids')):
    #                 break
    #             if vals.get('contacter_ids')[i][0] == 2:
    #                 del_contacter_ids.append(vals.get('contacter_ids')[i][1])
    #                 del vals.get('contacter_ids')[i]
    #             else:
    #                 i += 1
    #         for id in del_contacter_ids:
    #             self.env['customer.contacter'].browse(id).customer_id = False
    #     return vals





#客户联系人
class CustomerContacter(models.Model):
    _name = 'customer.contacter'
    _order = 'primary desc'

    name = fields.Char(string=u'姓名')
    email = fields.Char(string=u'邮箱')
    phone = fields.Char(string=u'电话', default='+')
    cellphone = fields.Char(string=u'手机', default='+')
    chuanzhen = fields.Char(string=u'传真')
    skype = fields.Char(string=u'skype')
    qq = fields.Char(string=u'QQ')
    wechat = fields.Char(string=u'WeChat')
    whatsapp = fields.Char(string=u'WhatsApp')
    other = fields.Char(string=u'其他联系方式')
    note = fields.Text(string=u'备注')
    primary = fields.Boolean(string=u'主联系人', default=True)
    image = fields.Binary("Image", attachment=True, help=u"照片不能超过1024*1024px")

    position = fields.Many2one('position', string=u'职位')
    customer_id = fields.Many2one('customer', string=u'客户', ondelete='cascade')

    #根据配置信息 检查联系人是否合法。如：姓名、邮箱是否唯一
    def check_contacter_legal(self, records):
        config = self.env['configuration'].sudo().browse(1)
        for record in records:
            #begin 一个客户只能有一个主联系人
            contacters = record.customer_id.contacter_ids
            primary_count = 0
            for contacter in contacters:
                if contacter.primary:
                    primary_count += 1
            if primary_count > 1:
                info = u'客户——%s，存在多个主联系人' % (record.customer_id.name)
                raise ValidationError(_(info))
            elif primary_count == 0:
                info = u'客户——%s，没有设置主联系人' % (record.customer_id.name)
                raise ValidationError(_(info))
            #end 一个客户只能有一个主联系人
            if config.contacter_name_unique and record.name:#姓名唯一
                results = self.sudo().search([('name','=',record.name),('id','!=',record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在联系人——%s，且该联系人当前负责人为——%s' % (results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_email_unique and record.email:#email唯一
                results = self.sudo().search([('email', '=', record.email), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在邮箱——%s，该邮箱所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].email, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_phone_unique and record.phone not in ['','+']:
                results = self.sudo().search([('phone', '=', record.phone), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在电话——%s，该电话所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].phone, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_cellphone_unique and record.cellphone not in ['','+']:
                results = self.sudo().search([('cellphone', '=', record.cellphone), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在手机号——%s，该手机号所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].cellphone, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_chuanzhen_unique and record.chuanzhen:
                results = self.sudo().search([('chuanzhen', '=', record.chuanzhen), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在传真——%s，该传真所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].chuanzhen, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_skype_unique and record.skype:
                results = self.sudo().search([('skype', '=', record.skype), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在skype——%s，该skype所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].skype, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_whatsapp_unique and record.whatsapp:
                results = self.sudo().search([('whatsapp', '=', record.whatsapp), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在whatsapp——%s，该whatsapp所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].whatsapp, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_wechat_unique and record.wechat:
                results = self.sudo().search([('wechat', '=', record.wechat), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在wechat——%s，该wechat所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].wechat, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_qq_unique and record.qq:
                results = self.sudo().search([('qq', '=', record.qq), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'系统中已存在qq——%s，该qq所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].qq, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))
            if config.contacter_other_unique and record.other:
                results = self.sudo().search([('other', '=', record.other), ('id', '!=', record.id)])
                if results and len(results) >= 1:
                    info = u'字段其他联系方式——%s，系统已存在，该联系方式所属联系人为——%s，该联系人的当前负责人为——%s' % \
                           (results[0].other, results[0].name, results[0].customer_id.salesman_id.name)
                    raise ValidationError(_(info))


    @api.model
    def create(self, vals):
        result = super(CustomerContacter, self).create(vals)
        # print 'create CustomerContacter', vals, result
        self.check_contacter_legal(result)
        return result

    @api.multi
    def write(self, vals):
        # print 'write CustomerContacter', vals
        result = super(CustomerContacter, self).write(vals)
        self.check_contacter_legal(self)
        return result

    #
    # @api.one
    # def _get_customer_id(self):
    #     for record in self:
    #         cus_con_rel_ids = record.customer_contact_rel_ids
    #         if cus_con_rel_ids:
    #             if len(cus_con_rel_ids) == 1:
    #                 record.customer_id = cus_con_rel_ids[0].customer_id.id
    #             elif len(cus_con_rel_ids) > 1:
    #                 info = u'该联系人对应多个客户！'
    #                 raise ValidationError(_(info))

    #获取联系人当地时间
    # @api.one
    # @api.depends('time_zone')
    # def _get_now_time(self):
    #     for record in self:
    #         del_hour = record.time_zone
    #         if del_hour:
    #             del_hour = int(del_hour) - 8#浏览器会再加8h
    #             record.now_time = datetime.datetime.now() + datetime.timedelta(hours=del_hour)
    #         else:
    #             record.now_time = datetime.datetime.now()

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

