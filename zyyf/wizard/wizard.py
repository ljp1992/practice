# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import xlrd,base64,datetime


class ImportWizard(models.TransientModel):
    _name = 'import.wizard'

    name = fields.Char(default=u'导入excel', string=u'')
    data = fields.Binary(string=u'文件')

    #检验工作表是否合法：表头是否正确；
    def check_sheet_legal(self, sheet):
        head = [u'客户名称',u'国家',u'详细地址',u'网址',u'开发时间',u'开发人',u'当前负责人',u'上次联系时间',u'间隔天数',u'下次联系时间',
                u'级别',u'类型',u'来源',u'状态',u'备注',u'联系人姓名',u'Email',u'电话',u'手机',u'传真',u'skype',u'WhatsApp',
                u'WeChat',u'QQ',u'其他联系方式',u'是否为主联系人',u'备注']
        for i in range(len(head)):
            val = sheet.cell(0, i).value
            if head[i] != val:
                info = u'工作表——%s，表头第%d列，应该为%s' % (sheet.name, i+1, head[i])
                raise ValueError(info)

    #读取excel数据 顺便检查表头是否正确
    #注意float类型数据
    def read_excel_data(self):
        if not self.data:
            raise UserError(u'请先上传文件')
        else:
            try:
                excel = xlrd.open_workbook(file_contents=base64.decodestring(self.data))
            except:
                raise UserError(u'请上传正确的excel文件')
            excel_data = []
            for i in range(len(excel.sheets())):
                sheet = excel.sheet_by_index(i)
                self.check_sheet_legal(sheet)
                if sheet.nrows <= 1:  #光有表头没有数据
                    continue
                if not sheet.cell(1, 0).value:
                    info = u'工作表——%s，第二行第一列缺少客户名称' % (sheet.name)
                    raise UserError(info)
                for row in range(1, sheet.nrows):
                    name = sheet.cell(row, 0).value
                    if name:
                        customer = {'row': row + 1,  # excel row
                                    'name': sheet.cell(row, 0).value,
                                    'country_id': sheet.cell(row, 1).value,
                                    'address': sheet.cell(row, 2).value,
                                    'website': sheet.cell(row, 3).value,
                                    'develop_time': sheet.cell(row, 4).value,
                                    'develop_id': sheet.cell(row, 5).value,
                                    'salesman_id': sheet.cell(row, 6).value,
                                    'last_contact_time': sheet.cell(row, 7).value,
                                    'interval_days': sheet.cell(row, 8).value,
                                    'next_contact_time': sheet.cell(row, 9).value,
                                    'grade_id': sheet.cell(row, 10).value,
                                    'type_id': sheet.cell(row, 11).value,
                                    'origin_id': sheet.cell(row, 12).value,
                                    'customer_state': sheet.cell(row, 13).value,
                                    'note': sheet.cell(row, 14).value,
                                    'contacter_ids': [],}
                        excel_data.append(customer)
                    contact_name = sheet.cell(row, 15).value
                    if contact_name:
                        contacter = {'row': row + 1,  # excel row
                                     'name': contact_name,
                                     'email': sheet.cell(row, 16).value,
                                     'phone': sheet.cell(row, 17).value,
                                     'cellphone': sheet.cell(row, 18).value,
                                     'chuanzhen': sheet.cell(row, 19).value,
                                     'skype': sheet.cell(row, 20).value,
                                     'whatsapp': sheet.cell(row, 21).value,
                                     'wechat': sheet.cell(row, 22).value,
                                     'qq': sheet.cell(row, 23).value,
                                     'other': sheet.cell(row, 24).value,
                                     'primary': sheet.cell(row, 25).value,
                                     'note': sheet.cell(row, 26).value,}
                        customer['contacter_ids'].append(contacter)
            return excel_data

    #解决excel 所有数字均为float类型的问题
    def handle_data_type(self, model, data):
        fields = self.env[model].fields_get()
        for (field, val) in data.items():
            if type(val) is float:
                if fields.has_key(field):
                    field_type = fields[field]['type']
                    if field_type == 'int':
                        data[field] = int(val)
                    elif field_type != 'float':
                        data[field] = str(int(val))
        return data

    #处理excel数据：开发时间为空，则设置为当前时间；格式化日期；
    def handle_excel_data(self, data):
        for m in range(len(data)):
            data[m] = self.handle_data_type('customer', data[m])
            for n in range(len(data[m]['contacter_ids'])):
                data[m]['contacter_ids'][n] = self.handle_data_type('customer.contacter', data[m]['contacter_ids'][n])
        customer_obj = self.env['customer']
        contacter_obj = self.env['customer.contacter']
        uesr_obj = self.env['res.users']
        country_obj = self.env['country']
        grade_obj = self.env['customer.grade']
        type_obj = self.env['customer.type']
        origin_obj = self.env['customer.origin']
        state_obj = self.env['customer.state']
        for vals in data:
            if vals['country_id']:
                countrys = country_obj.sudo().search([('name', '=', vals['country_id'])])
                if countrys:
                    vals['country_id'] = countrys[0].id
                else:
                    vals['country_id'] = country_obj.create({'name': vals['country_id']}).id
            else:
                vals['country_id'] = False
            if vals['develop_time']:
                vals['develop_time'] = vals['develop_time'].replace('/','-')
            else:
                vals['develop_time'] = datetime.datetime.now()
            if vals['develop_id']:
                users = uesr_obj.sudo().search([('name', '=', vals['develop_id'])])
                if users:
                    vals['develop_id'] = users[0].id
                else:
                    info = u'系统不存在用户——%s' % (vals['develop_id'])
                    raise UserError(info)
            else:
                vals['develop_id'] = self.env.user.id
            if vals['salesman_id']:
                users = uesr_obj.sudo().search([('name', '=', vals['salesman_id'])])
                if users:
                    vals['salesman_id'] = users[0].id
                else:
                    info = u'系统不存在用户——%s' % (vals['salesman_id'])
                    raise UserError(info)
            else:
                vals['salesman_id'] = self.env.user.id
            if vals['last_contact_time']:
                vals['last_contact_time'] = vals['last_contact_time'].replace('/', '-')
            else:
                vals['last_contact_time'] = datetime.datetime.now()
            if not vals['interval_days']:
                vals['interval_days'] = 0
            if vals['next_contact_time']:
                vals['next_contact_time'] = vals['next_contact_time'].replace('/', '-')
            else:
                vals['next_contact_time'] = datetime.datetime.now()
            if vals['grade_id']:
                results = grade_obj.sudo().search([('name', '=', vals['grade_id'])])
                if results:
                    vals['grade_id'] = results[0].id
                else:
                    vals['grade_id'] = grade_obj.create({'name': vals['grade_id']}).id
            else:
                vals['grade_id'] = False
            if vals['type_id']:
                results = type_obj.sudo().search([('name', '=', vals['type_id'])])
                if results:
                    vals['type_id'] = results[0].id
                else:
                    vals['type_id'] = type_obj.create({'name': vals['type_id']}).id
            else:
                vals['type_id'] = False
            if vals['origin_id']:
                results = origin_obj.sudo().search([('name', '=', vals['origin_id'])])
                if results:
                    vals['origin_id'] = results[0].id
                else:
                    vals['origin_id'] = origin_obj.create({'name': vals['origin_id']}).id
            else:
                vals['origin_id'] = False
            if vals['customer_state']:
                results = state_obj.sudo().search([('name', '=', vals['customer_state'])])
                if results:
                    vals['customer_state'] = results[0].id
                else:
                    vals['customer_state'] = state_obj.create({'name': vals['customer_state']}).id
            else:
                vals['customer_state'] = False
            if vals['contacter_ids']:
                for j in range(len(vals['contacter_ids'])):
                    contacter = vals['contacter_ids'][j]
                    if contacter['primary'] == u'是':
                        contacter['primary'] = True
                    else:
                        contacter['primary'] = False
                    vals['contacter_ids'][j] = contacter
        return data

    # 创建客户
    def create_customer_by_data(self, data):
        customer_obj = self.env['customer']
        for customer in data:
            if customer.has_key('row'):
                customer.pop('row')
            for j in range(len(customer['contacter_ids'])):
                contacter = customer['contacter_ids'][j]
                if contacter.has_key('row'):
                    contacter.pop('row')
                customer['contacter_ids'][j] = [0, False, contacter]
            customer_obj.create(customer)

    #导入客户资料excel
    def import_customer_excel(self):
        excel_data = self.read_excel_data()
        data = self.handle_excel_data(excel_data)
        self.create_customer_by_data(data)

    #下载模板文件
    def download_template_file(self):
        # self.env['excel.template'].sudo().serach()
        url = '/web/binary/download_document/?model=excel.template&field=template_file&id=%d&filename=%s' % (1, u'客户模板.xlsx')
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

