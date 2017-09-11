# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CustomerConfiguration(models.Model):
    _name = 'customer.configuration'
    _rec_name = 'title'

    title = fields.Char(default=u'客户')
    #form 唯一项
    form_name_unique = fields.Boolean(string=u'客户名称', default=True)
    form_website_unique = fields.Boolean(string=u'网址')
    #form 显示／隐藏项
    form_develop_id_invisible = fields.Boolean(string=u'开发人')
    #必填项
    form_name_required = fields.Boolean(string=u'客户名称',default=True)
    form_country_id_required = fields.Boolean(string=u'国家')
    form_website_required = fields.Boolean(string=u'网址')
    form_address_required = fields.Boolean(string=u'详细地址')
    form_develop_time_required = fields.Boolean(string=u'开发时间')
    form_develop_id_required = fields.Boolean(string=u'开发人')
    form_salesman_id_required = fields.Boolean(string=u'当前负责人')
    form_last_contact_time_required = fields.Boolean(string=u'上次联系时间')
    form_interval_days_required = fields.Boolean(string=u'间隔天数')
    form_next_contact_time_required = fields.Boolean(string=u'下次联系时间')
    form_grade_id_required = fields.Boolean(string=u'级别')
    form_type_id_required = fields.Boolean(string=u'类型')
    form_origin_id_required = fields.Boolean(string=u'来源')
    form_customer_state_required = fields.Boolean(string=u'状态')
    #tree 显示／隐藏
    tree_country_id_invisible = fields.Boolean(string=u'国家')
    tree_website_invisible = fields.Boolean(string=u'网址')
    tree_address_invisible = fields.Boolean(string=u'详细地址')
    tree_develop_time_invisible = fields.Boolean(string=u'开发时间')
    tree_develop_id_invisible = fields.Boolean(string=u'开发人')
    tree_salesman_id_invisible = fields.Boolean(string=u'当前负责人')
    tree_last_contact_time_invisible = fields.Boolean(string=u'上次联系时间')
    tree_interval_days_invisible = fields.Boolean(string=u'间隔天数')
    tree_next_contact_time_invisible = fields.Boolean(string=u'下次联系时间')
    tree_grade_id_invisible = fields.Boolean(string=u'级别')
    tree_type_id_invisible = fields.Boolean(string=u'类型')
    tree_origin_id_invisible = fields.Boolean(string=u'来源')
    tree_customer_state_invisible = fields.Boolean(string=u'状态')
    #other
    form_contacter_required = fields.Boolean(string=u'联系人不能为空')

    @api.onchange('form_develop_id_invisible')
    def onchange_form_develop_id_show(self):
        for record in self:
            if record.form_develop_id_invisible:
                record.form_develop_id_required = False

    def get_config(self):

        fields = ['name', 'country_id', 'address', 'website', 'develop_time', 'develop_id', 'salesman_id',
                  'last_contact_time', 'interval_days', 'next_contact_time', 'grade_id', 'type_id',
                  'origin_id', 'customer_state']
        config = self.sudo().browse(1).read()[0]
        print config

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CustomerConfiguration, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        self.get_config()
        return res
    
    # #获取唯一性字段
    def get_unique_fields(self):
        fields = ['name','website']
        unique_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            unique_field = 'form_' + field + '_unique'
            if config.get(unique_field):
                unique_fields.append(field)
        return unique_fields

    # 获取必填字段
    def get_required_fields(self):
        fields = ['name', 'country_id', 'address', 'website', 'develop_time', 'develop_id', 'salesman_id',
                  'last_contact_time', 'interval_days', 'next_contact_time', 'grade_id', 'type_id',
                  'origin_id', 'customer_state']
        required_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            required_field = 'form_' + field + '_required'
            if config.get(required_field):
                required_fields.append(field)
        return required_fields

    #form需要隐藏的字段
    def get_form_invisible_fields(self):
        fields = ['develop_id']
        invisible_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            invisible_field = 'form_' + field + '_invisible'
            if config.get(invisible_field):
                invisible_fields.append(field)
        return invisible_fields

    # tree需要隐藏的字段
    def get_tree_invisible_fields(self):
        fields = ['country_id', 'address', 'website', 'develop_time', 'develop_id', 'salesman_id',
                  'last_contact_time', 'interval_days', 'next_contact_time', 'grade_id', 'type_id',
                  'origin_id', 'customer_state']
        invisible_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            invisible_field = 'tree_' + field + '_invisible'
            if config.get(invisible_field):
                invisible_fields.append(field)
        return invisible_fields

