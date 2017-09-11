# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from lxml import etree
import json

#客户联系人
class CustomerContacter(models.Model):
    _name = 'customer.contacter'
    # _order = 'primary desc'

    name = fields.Char(string=u'联系人姓名')
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

    position_id = fields.Many2one('position', string=u'职位')
    customer_id = fields.Many2one('customer', string=u'所属客户', ondelete='cascade')

    # 设置form必填项
    def set_form_field_required(self, doc):
        required_fields = self.env['contacter.configuration'].get_required_fields()
        for field in required_fields:
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                modifiers = json.loads(node.get("modifiers"))
                modifiers['required'] = True
                node.set("modifiers", json.dumps(modifiers))

    def set_form_field_invisible(self, doc):
        invisible_fields = self.env['contacter.configuration'].get_form_invisible_fields()
        for field in invisible_fields:
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                modifiers = json.loads(node.get("modifiers"))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

    def set_other_field_attr(self, doc):
        pass

    def set_tree_field_invisible(self, doc):
        invisible_fields = self.env['contacter.configuration'].get_tree_invisible_fields()
        for field in invisible_fields:
            xpath_val = "//field[@name='%s']" % (field)
            for node in doc.xpath(xpath_val):
                modifiers = json.loads(node.get("modifiers"))
                modifiers['tree_invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CustomerContacter, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        # print 'contacter', view_id, res['arch']
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            self.set_form_field_required(doc)  # 设置form必填项
            self.set_form_field_invisible(doc)
            self.set_other_field_attr(doc)
        elif view_type == 'tree':
            self.set_tree_field_invisible(doc)
        res['arch'] = etree.tostring(doc)
        return res

    # unique检查
    def check_unique(self, records):
        unique_fields = self.env['contacter.configuration'].get_unique_fields()
        fields_info = self.fields_get()
        for record in records:
            for field in unique_fields:
                val = record.read([field])[0][field]
                if not val:
                    continue
                if field in ['phone','cellphone'] and val == u'+':
                    continue
                results = self.sudo().search([(field, '=', val), ('id', '!=', record.id)])
                if results:
                    info = u'%s-%s，系统已存在' % (fields_info.get(field).get('string'), val)
                    raise UserError(info)

    @api.model
    def create(self, vals):
        result = super(CustomerContacter, self).create(vals)
        # print 'create CustomerContacter', vals, result
        # self.check_contacter_legal(result)
        self.check_unique(result)# unique检查
        return result

    @api.multi
    def write(self, vals):
        # print 'write CustomerContacter', vals
        result = super(CustomerContacter, self).write(vals)
        # self.check_contacter_legal(self)
        self.check_unique(self)# unique检查
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
