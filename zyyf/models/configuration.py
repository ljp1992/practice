# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Configuration(models.Model):
    _name = 'configuration'

    name = fields.Char(default=u'设置')
    customer_name_unique = fields.Boolean(u'客户名称唯一')
    customer_website_unique = fields.Boolean(u'网址唯一')
    customer_country_required = fields.Boolean(u'国家必填')
    customer_website_required = fields.Boolean(u'网址必填')
    import_customer_data = fields.Selection(selection=[('no_cover',u'若excel中的数据与系统原有数据发生冲突，则导出冲突数据'),
                                                        ('cover',u'若excel中的数据与系统原有数据发生冲突，则覆盖系统中的数据')],
                                             string=u'客户资料excel导入')
    contacter_name_unique = fields.Boolean(u'姓名唯一')
    contacter_email_unique = fields.Boolean(u'email唯一')
    contacter_phone_unique = fields.Boolean(u'电话唯一')
    contacter_cellphone_unique = fields.Boolean(u'手机唯一')
    contacter_chuanzhen_unique = fields.Boolean(u'传真唯一')
    contacter_skype_unique = fields.Boolean(u'skype唯一')
    contacter_whatsapp_unique = fields.Boolean(u'whatsapp唯一')
    contacter_wechat_unique = fields.Boolean(u'wechat唯一')
    contacter_qq_unique = fields.Boolean(u'qq唯一')
    contacter_other_unique = fields.Boolean(u'其他联系方式唯一')
    so_jiaohuo_remind = fields.Integer(string=u'销售订单交货日期提醒')
