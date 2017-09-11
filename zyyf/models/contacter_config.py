# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time


class CustomerConfiguration(models.Model):
    _name = 'contacter.configuration'
    _rec_name = 'title'

    title = fields.Char(default=u'联系人')
    # form 唯一项
    form_name_unique = fields.Boolean(string=u'姓名', default=True)
    form_email_unique = fields.Boolean(string=u'Email', default=True)
    form_phone_unique = fields.Boolean(string=u'电话', default=True)
    form_cellphone_unique = fields.Boolean(string=u'手机', default=True)
    form_chuanzhen_unique = fields.Boolean(string=u'传真', default=True)
    form_skype_unique = fields.Boolean(string=u'Skype', default=True)
    form_qq_unique = fields.Boolean(string=u'QQ', default=True)
    form_wechat_unique = fields.Boolean(string=u'WeChat', default=True)
    form_whatsapp_unique = fields.Boolean(string=u'WhatsApp', default=True)
    form_other_unique = fields.Boolean(string=u'其他联系方式', default=True)
    # form 显示／隐藏项
    
    # 必填项
    form_name_required = fields.Boolean(string=u'姓名', default=True)
    form_position_id_required = fields.Boolean(string=u'职位')
    form_email_required = fields.Boolean(string=u'Email')
    form_phone_required = fields.Boolean(string=u'电话')
    form_cellphone_required = fields.Boolean(string=u'手机')
    form_chuanzhen_required = fields.Boolean(string=u'传真')
    form_skype_required = fields.Boolean(string=u'Skype')
    form_qq_required = fields.Boolean(string=u'QQ')
    form_wechat_required = fields.Boolean(string=u'WeChat')
    form_whatsapp_required = fields.Boolean(string=u'WhatsApp')
    # tree 显示／隐藏
    tree_email_invisible = fields.Boolean(string=u'Email')
    tree_position_id_invisible = fields.Boolean(string=u'职位')
    tree_phone_invisible = fields.Boolean(string=u'电话')
    tree_cellphone_invisible = fields.Boolean(string=u'手机', default=True)
    tree_chuanzhen_invisible = fields.Boolean(string=u'传真', default=True)
    tree_skype_invisible = fields.Boolean(string=u'Skype', default=True)
    tree_qq_invisible = fields.Boolean(string=u'QQ', default=True)
    tree_wechat_invisible = fields.Boolean(string=u'WeChat', default=True)
    tree_whatsapp_invisible = fields.Boolean(string=u'WhatsApp', default=True)
    tree_other_invisible = fields.Boolean(string=u'其他联系方式', default=True)
    tree_note_invisible = fields.Boolean(string=u'备注', default=True)
    # other
    # form_contacter_required = fields.Boolean(string=u'创建编辑联系人时，必须填写联系人')

    # #获取唯一性字段
    def get_unique_fields(self):
        fields = ['name', 'email', 'phone', 'cellphone', 'chuanzhen', 'skype', 'qq', 'wechat', 'whatsapp', 'other']
        unique_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            unique_field = 'form_' + field + '_unique'
            if config.get(unique_field):
                unique_fields.append(field)
        return unique_fields

    # 获取必填字段
    def get_required_fields(self):
        fields = ['name', 'position_id', 'email', 'phone', 'cellphone', 'chuanzhen', 'skype', 'qq', 'wechat',
                  'whatsapp']
        required_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            required_field = 'form_' + field + '_required'
            if config.get(required_field):
                required_fields.append(field)
        return required_fields

    #form需要隐藏的字段
    def get_form_invisible_fields(self):
        # fields = []
        # invisible_fields = []
        # config = self.sudo().browse(1).read()[0]
        # for field in fields:
        #     invisible_field = 'form_' + field + '_invisible'
        #     if config.get(invisible_field):
        #         invisible_fields.append(field)
        return []

    #tree需要隐藏的字段
    def get_tree_invisible_fields(self):
        fields = ['position_id', 'email', 'phone', 'cellphone', 'chuanzhen', 'skype', 'qq', 'wechat',
                  'whatsapp', 'other', 'note']
        invisible_fields = []
        config = self.sudo().browse(1).read()[0]
        for field in fields:
            invisible_field = 'tree_' + field + '_invisible'
            if config.get(invisible_field):
                invisible_fields.append(field)
        return invisible_fields

    @api.multi
    def write(self, vals):
        result = super(CustomerConfiguration, self).write(vals)
        return result
