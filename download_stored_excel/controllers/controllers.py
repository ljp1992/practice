# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition
import json,base64

class Crm(http.Controller):

    #下载excel文件。传入model id field filename,从数据库取出存储的文件
    @http.route(['/web/binary/download_document'], type='http', auth='public')
    def download_stored_excel(self, **kwargs):
        model = kwargs.get('model')
        field = kwargs.get('field')
        id = kwargs.get('id')
        print id,type(id)
        if type(id) is not int:
            id = int(id)
        # id = json.loads(kwargs.get('id'))
        filename = kwargs.get('filename')
        res = request.env[model].sudo().browse(id)
        if res:
            res = res.read()
            filecontent = base64.b64decode(res[0].get(field) or '')
            if filecontent and filename:
                return request.make_response(filecontent, [('Content-Type', 'application/octet-stream'),
                                                           ('Content-Disposition', content_disposition(filename))])
        else:
            return request.not_found()


