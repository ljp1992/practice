# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import xlrd, xlwt, base64, datetime
from cStringIO import StringIO

class ExcelTemplate(models.Model):
    _name = 'excel.template'

    name = fields.Char(string=u'模板名称')
    template_file = fields.Binary(string=u'模板文件')

    #下载模板文件
    # @api.multi
    def download_template_file(self):
        model = 'excel.template'
        field = 'template_file'
        id = self.id
        filename = u'测试.xlsx'
        return {
            'type': 'ir.actions.client',
            'tag': 'upload_download_excel',
            'context': {'model': model,
                        'field': field,
                        'id':id,
                        'filename':filename,
                        }
        }

class ImportWizard(models.TransientModel):
    _name = 'import.wizard'

    # name = fields.Char(default=u'导入excel', string=u'')
    data = fields.Binary(string=u'文件')