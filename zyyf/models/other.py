# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import xlrd, xlwt, base64, datetime
from cStringIO import StringIO



#国家
class Country(models.Model):
    _name = 'country'

    name = fields.Char(string=u'国家')
    note = fields.Text(string=u'备注')


#职位
class Position(models.Model):
    _name = 'position'

    name = fields.Char(string=u'职位')
    note = fields.Text(string=u'备注')

class ExcelTemplate(models.Model):
    _name = 'excel.template'

    name = fields.Char(string=u'模板名称')
    template_file = fields.Binary(string=u'模板文件')

    #导入数据
    def upload_template_file(self):
        if self.data:
            try:
                excel = xlrd.open_workbook(file_contents=base64.decodestring(self.data))
            except:
                raise UserError(u'上传的文件不是excel文件')
        else:
            raise UserError(u'请先上传文件')

    #下载模板文件
    # @api.multi
    def download_template_file(self):
        model = 'excel.template'
        field = 'template_file'
        id = 1
        filename = u'客户资料模板.xlsx'
        return {
            'type': 'ir.actions.client',
            'tag': 'download_excel_ljp',
            'context': {'model': model,
                        'field': field,
                        'id':id,
                        'filename':filename,
                        }
        }
        # url = '/web/binary/download_document/?model=excel.template&field=template_file&id=%d&filename=%s' % (self.id, u'客户模板.xlsx')
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': url,
        #     'target': 'self',
        # }

    # def download_template_file_xlwt(self):
    #     excel = xlwt.Workbook()
    #     sheet1 = excel.add_sheet(u'业务员张三', cell_overwrite_ok=True)
    #     sheet1.write(0,0,u'客户名称')
    #     sheet1.write(1,0,u'联系人王五')
    #     # excel.save(u'cs.xlsx')
    #
    #     fp = StringIO()
    #     print fp
    #     excel.save(fp)
    #     fp.seek(0)
    #     data = fp.read()
    #     fp.close()
    #     print data
    #     return data

# time_zone = fields.Selection(selection=[('-11',u'UTC-11'),
    #                                        ('-10', u'UTC-10'),
    #                                        ('-9', u'UTC-9'),
    #                                        ('-8', u'UTC-8'),
    #                                        ('-7', u'UTC-7'),
    #                                        ('-6', u'UTC-6'),
    #                                        ('-5', u'UTC-5'),
    #                                        ('-4', u'UTC-4'),
    #                                        ('-3', u'UTC-3'),
    #                                        ('-2', u'UTC-2'),
    #                                        ('-1', u'UTC-1'),
    #                                        ('0', u'UTC'),
    #                                        ('+1', u'UTC+1'),
    #                                        ('+2', u'UTC+2'),
    #                                        ('+3', u'UTC+3'),
    #                                        ('+4', u'UTC+4'),
    #                                        ('+5', u'UTC+5'),
    #                                        ('+6', u'UTC+6'),
    #                                        ('+7', u'UTC+7'),
    #                                        ('+8', u'UTC+8'),
    #                                        ('+9', u'UTC+9'),
    #                                        ('+10', u'UTC+10'),
    #                                        ('+11', u'UTC+11'),],string=u'时区')
    # now_time = fields.Datetime(u'当地时间', compute='_get_now_time', store=False)

# #省／州
# class Province(models.Model):
#     _name = 'province'
#
#     name = fields.Char(string=u'省／州')
#     country_id = fields.Many2one('country', u'国家')
#     note = fields.Text(string=u'备注')
#
# #市
# class City(models.Model):
#     _name = 'city'
#
#     name = fields.Char(string=u'市')
#     note = fields.Text(string=u'备注')
#     province_id = fields.Many2one('province', u'省／州')

# #街道。。。
# class Street(models.Model):
#     _name = 'street'
#
#     name = fields.Char(string=u'街道')
#     note = fields.Text(string=u'备注')
#     city_id = fields.Many2one('city', u'市')

# #称谓
# class CustomerCall(models.Model):
#     _name = 'customer.call'
#
#     name = fields.Char(string=u'称谓')
#     note = fields.Text(string=u'备注')