# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import xlrd,base64,datetime


class ImportWizard(models.TransientModel):
    _name = 'import.wizard'

    name = fields.Char(default=u'导入excel', string=u'')
    data = fields.Binary(string=u'文件')

    #导入客户资料excel
    def import_customer_excel(self):
        excel = self.get_excel_file()#获取导入的excel，若没有获取到，给出提示
        self.get_right_excel_head()#正确的模板表头，以及各列对应的field,model,type,unique,required
        self.check_import_excel_head(excel)#检查导入的excel，表头是否合法
        excel_data = self.get_excel_data(excel)#获取excel数据
        # print excel_data
        self.check_excel_data(excel_data)
        self.create_customer_by_data(excel_data)


    #检查excel 各个sheet head是否合法
    def check_import_excel_head(self, excel):
        for i in range(len(excel.sheets())):
            sheet = excel.sheet_by_index(i)
            if sheet.nrows == 0:
                continue
            import_head = sheet.row_values(0)
            if import_head[0] != u'客户名称':  # 表头第一列必须是客户名称
                info = u'工作表-%s，表头第一列必须为-%s' % (sheet.name, u'客户名称')
                raise UserError(info)
            head_dic = {}
            for i in range(len(import_head)):  # 有没有重复列
                val = import_head[i]
                if not val:
                    continue
                if head_dic.has_key(val):
                    j = head_dic[val]['col']
                    info = u'工作表-%s，表头第%d列与第%d列名称重复，都为-%s！' % (sheet.name, i + 1, j + 1, val)
                    raise UserError(info)
                else:
                    head_dic[val] = ''
            for (key, val) in head_dic.items():  # 检查该工作表的表头 各列是否存在
                if not self.right_head.has_key(key):
                    info = u'工作表-%s，表头第%d列-%s，模板中不存在该列！' % (sheet.name, val.get('col') + 1, key)
                    raise UserError(info)
            for (key, val) in self.right_head.items():  # 检查该工作表是否缺少某一列
                if not head_dic.has_key(key):
                    info = u'工作表-%s，表头缺少列-%s' % (sheet.name, key)
                    raise UserError(info)

    def get_customer_cols(self):
        customer_cols = []
        for (col, val) in self.sheet_col_info.items():
            val = self.sheet_col_info[col]
            if val['model'] == 'customer':
                customer_cols.append(col)
        customer_cols.sort()
        return customer_cols

    def get_contacter_cols(self):
        contacter_cols = []
        for (col, val) in self.sheet_col_info.items():
            val = self.sheet_col_info[col]
            if val['model'] == 'customer.contacter':
                contacter_cols.append(col)
        contacter_cols.sort()
        return contacter_cols

    def get_sheet_col_info(self, sheet):
        self.sheet_col_info = {}
        sheet_head = sheet.row_values(0)
        for col in range(len(sheet_head)):
            if sheet_head[col]:
                if self.right_head.has_key(sheet_head[col]):
                    val = self.right_head[sheet_head[col]]
                    self.sheet_col_info[col] = {'head_name':sheet_head[col],
                                               'field':val['field'],
                                               'model':val['model'],
                                               'type':val['type'],
                                               'required':val['required'],
                                               'unique':val['unique'],}

    def get_contacter_name_col(self):
        for (col, val) in self.sheet_col_info.items():
            if val['model'] == 'customer.contacter' and val['field'] == 'name':
                return col

    #读取excel数据
    def get_excel_data(self, excel):
        excel_data = []
        for i in range(len(excel.sheets())):
            sheet = excel.sheet_by_index(i)
            if sheet.nrows <= 1:
                continue
            if not sheet.cell(1, 0).value:
                info = u'工作表—%s，第二行第一列缺少客户名称' % (sheet.name)
                raise UserError(info)
            self.get_sheet_col_info(sheet)#每列对应的信息
            customer_cols = self.get_customer_cols()#客户是哪些列
            contacter_cols = self.get_contacter_cols()#联系人是哪些列
            contacter_name_col = self.get_contacter_name_col()#获取联系人姓名是哪一列
            for row in range(1, sheet.nrows):
                customer_name = self.handle_excel_cell_val(sheet, row, 0)
                if customer_name:
                    customer = {'row': row, 'sheet_name':sheet.name, 'contacter_ids': []}
                    excel_data.append(customer)
                    for col in customer_cols:
                        customer.update(
                            {self.sheet_col_info[col]['field']: self.handle_excel_cell_val(sheet, row, col)}
                        )
                contacter_name = self.handle_excel_cell_val(sheet, row, contacter_name_col)
                if contacter_name:
                    contacter = {'row': row, 'sheet_name':sheet.name,}
                    for col in contacter_cols:
                        contacter.update(
                            {self.sheet_col_info[col]['field']: self.handle_excel_cell_val(sheet, row, col)}
                        )
                    customer['contacter_ids'].append(contacter)
        return excel_data

    #正确的模板表头内容
    def get_right_excel_head(self):
        head = {u'客户名称':{'field':'name','model':'customer'},
                u'国家':{'field':'country_id','model':'customer'},
                u'详细地址':{'field':'address','model':'customer'},
                u'网址':{'field':'website','model':'customer'},
                u'开发时间':{'field':'develop_time','model':'customer'},
                u'开发人':{'field':'develop_id','model':'customer'},
                u'当前负责人':{'field':'salesman_id','model':'customer'},
                u'上次联系时间':{'field':'last_contact_time','model':'customer'},
                u'间隔天数':{'field':'interval_days','model':'customer'},
                u'下次联系时间':{'field':'next_contact_time','model':'customer'},
                u'级别':{'field':'grade_id','model':'customer'},
                u'类型':{'field':'type_id','model':'customer'},
                u'来源':{'field':'origin_id','model':'customer'},
                u'客户状态':{'field':'customer_state','model':'customer'},
                u'客户备注':{'field':'note','model':'customer'},
                u'联系人姓名':{'field':'name','model':'customer.contacter'},
                u'是否为主联系人': {'field':'primary','model':'customer.contacter'},
                u'Email':{'field':'email','model':'customer.contacter'},
                u'电话':{'field':'phone','model':'customer.contacter'},
                u'手机':{'field':'cellphone','model':'customer.contacter'},
                u'传真':{'field':'chuanzhen','model':'customer.contacter'},
                u'skype':{'field':'skype','model':'customer.contacter'},
                u'WhatsApp':{'field':'whatsapp','model':'customer.contacter'},
                u'WeChat':{'field':'wechat','model':'customer.contacter'},
                u'QQ':{'field':'qq','model':'customer.contacter'},
                u'其他联系方式':{'field':'other','model':'customer.contacter'},
                u'联系人备注':{'field':'note','model':'customer.contacter'},
        }
        self.customer_fields = self.env['customer'].fields_get()
        self.contacter_fields = self.env['customer.contacter'].fields_get()
        config = self.env['configuration'].sudo().browse(1)
        for (key, val) in head.items():#设置每列的 type unique required
            field = val['field']
            val['required'] = False
            val['unique'] = False
            val['vals'] = {}
            if val['model'] == 'customer':
                val['type'] = self.customer_fields[field]['type']
                if val['field'] == 'name':
                    val['required'] = True
                    val['unique'] = True
                elif val['field'] == 'country_id':
                    if config.customer_country_required:
                        val['required'] = True
                elif val['field'] == 'website':
                    if config.customer_website_required:
                        val['required'] = True
                    if config.customer_website_unique:
                        val['unique'] = True
            elif val['model'] == 'customer.contacter':
                val['type'] = self.contacter_fields[field]['type']
                if val['field'] == 'name':
                    val['required'] = True
                    val['unique'] = True
                elif val['field'] == 'email':
                    if config.contacter_email_unique:
                        val['unique'] = True
        self.right_head = head

    def get_excel_file(self):
        if self.data:
            try:
                excel = xlrd.open_workbook(file_contents=base64.decodestring(self.data))
                return excel
            except:
                raise UserError(u'请上传正确的excel文件')
        else:
            raise UserError(u'请先上传文件')


    #如果是整数类型 excel中为float 则int()
    def handle_excel_cell_val(self, sheet, row, col):
        val = sheet.cell(row, col).value
        if type(val) is not unicode:
            info = u'工作表-%s，第%d行第%d列单元格格式不是文本类型，请设置整个excel的单元格格式为文本类型！' % (sheet.name, row+1, col+1)
            raise ValueError(info)
        head_name = self.sheet_col_info[col]['head_name']
        field_type = self.sheet_col_info[col]['type']
        model = self.sheet_col_info[col]['model']
        field = self.sheet_col_info[col]['field']
        if field_type in ['datetime', 'date']:
            val = self.handle_datetime(sheet, row, col, val)
            print field,val
        elif field_type == 'many2one':
            if not val:
                return False
            if model == 'customer':
                relation_model = self.customer_fields.get(field).get('relation')
                results = self.env[relation_model].sudo().search([('name','=',val)])
                if results:
                    val = results[0].id
                else:
                    if field in ['develop_id','salesman_id']:
                        info = u'工作表-%s，第%s行%s-%s，系统不存在该%s！' % (sheet.name, row+1, head_name, val, head_name)
                        raise UserError(info)
                    else:
                        val = self.env[relation_model].create({'name':val}).id
        elif field_type == 'integer':
            if not val:
                return 0
            try:
                val = int(val)
            except:
                info = u'工作表-%s，第%s行%s-%s，不是数字！'  % (sheet.name, row, head_name, val)
                raise UserError(info)
        elif field_type == 'boolean':
            if val == u'是':
                val = True
            elif val == '':
                val = False
            else:
                info = u'工作表-%s，第%s行%s-%s，只能填是或不填！' % (sheet.name, row, head_name, val)
                raise UserError(info)
        return val

    def get_contacter_fields_info(self):
        contacter_fields_info = {}
        for (head_name, val) in self.right_head.items():
            if val['model'] == 'customer.contacter':
                contacter_fields_info[val['field']] = {'head_name': head_name,
                                                       'required': val['required'],
                                                       'unique': val['unique'],
                                                       'vals': {},}
        return contacter_fields_info

    def get_customer_fields_info(self):
        customer_fields_info = {}
        for (head_name, val) in self.right_head.items():
            if val['model'] == 'customer':
                customer_fields_info[val['field']] = {'head_name': head_name,
                                                      'required': val['required'],
                                                      'unique': val['unique'],
                                                      'vals': {},}
        return customer_fields_info

    def check_excel_data(self, excel_data):
        self.customer_fields_info = self.get_customer_fields_info()
        self.contacter_fields_info = self.get_contacter_fields_info()
        for customer in excel_data:
            for (field, val) in customer.items():
                if self.customer_fields_info.has_key(field):
                    field_attr = self.customer_fields_info[field]
                    if field_attr['required'] and not val:
                        info = u'工作表-%s，第%s行%s不能为空！' % (customer['sheet_name'], customer['row']+1, field_attr['head_name'])
                        raise UserError(info)
                    if val and field_attr['unique']:
                        if field_attr['vals'].has_key(val):
                            info = u'工作表-%s，第%s行与第%s行%s重复！' % \
                                   (customer['sheet_name'], field_attr['vals'][val], customer['row']+1, field_attr['head_name'])
                            raise UserError(info)
                        else:
                            self.customer_fields_info[field]['vals'].update({val:customer['row']})
                        results = self.env['customer'].sudo().search([(field,'=',val)])
                        if results:
                            info = u'工作表-%s，第%s行%s-%s，系统已存在！' % \
                                   (customer['sheet_name'], customer['row']+1, field_attr['head_name'], val)
                            raise UserError(info)
            contacters = customer['contacter_ids']
            primary_count = 0
            for contacter in contacters:
                for (field, val) in contacter.items():
                    if field == 'primary' and val:
                        print '+1'
                        primary_count += 1
                    if self.contacter_fields_info.has_key(field):
                        field_attr = self.contacter_fields_info[field]
                        if field_attr['required'] and not val:
                            info = u'工作表-%s，第%s行%s不能为空！' % \
                                   (contacter['sheet_name'], contacter['row'] + 1, field_attr['head_name'])
                            raise UserError(info)
                        if val and field_attr['unique']:
                            if field_attr['vals'].has_key(val):
                                info = u'工作表-%s，第%s行与第%s行%s重复！' % \
                                       (contacter['sheet_name'], field_attr['vals'][val]+1, contacter['row'] + 1,
                                        field_attr['head_name'])
                                raise UserError(info)
                            else:
                                self.contacter_fields_info[field]['vals'].update({val:contacter['row']})
                            results = self.env['customer.contacter'].sudo().search([(field,'=',val)])
                            if results:
                                info = u'工作表-%s，第%s行%s-%s，系统已存在！' % \
                                       (contacter['sheet_name'], contacter['row']+1, field_attr['head_name'], val)
                                raise UserError(info)

            if contacters:
                if primary_count == 0:
                    info = u'工作表-%s，第%s行,没有为该客户设置主联系人' % \
                           (customer['sheet_name'], customer['row']+1)
                    raise UserError(info)
                elif primary_count > 1:
                    info = u'工作表-%s，第%s行,该客户设置了多个主联系人' % \
                           (customer['sheet_name'], customer['row']+1)
                    raise UserError(info)

    # 处理日期字段
    def handle_datetime(self, sheet, row, col, val):
        if not val:
            return False
        result = False
        temp = val.split(' ')
        if len(temp) == 1:  # date
            try:
                result = datetime.datetime.strptime(val, '%Y-%m-%d')
                result = result.strftime('%Y-%m-%d %H:%M:%S')
            except:
                try:
                    result = datetime.datetime.strptime(val, '%Y/%m/%d')
                    result = result.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    info = u'工作表-%s，第%s行第%s列，日期不合法！' % (sheet.name, row, col)
                    raise ValueError(info)
        elif len(temp) == 2:
            try:
                result = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    result = datetime.datetime.strptime(val, '%Y/%m/%d %H:%M:%S')
                except:
                    info = u'工作表-%s，第%s行第%s列，日期不合法！' % (sheet.name, row, col)
                    raise ValueError(info)
        else:
            info = u'工作表-%s，第%s行第%s列，日期不合法！' % (sheet.name, row, col)
            raise ValueError(info)
        return result

    # 创建客户
    def create_customer_by_data(self, data):
        customer_obj = self.env['customer']
        for customer in data:
            if customer.has_key('row'):
                customer.pop('row')
            if customer.has_key('sheet_name'):
                customer.pop('sheet_name')
            for j in range(len(customer['contacter_ids'])):
                contacter = customer['contacter_ids'][j]
                if contacter.has_key('row'):
                    contacter.pop('row')
                if contacter.has_key('sheet_name'):
                    contacter.pop('sheet_name')
                customer['contacter_ids'][j] = [0, False, contacter]
            # print customer
            customer_obj.create(customer)

    #下载模板文件
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
                        'id': id,
                        'filename': filename,
                        }
        }
