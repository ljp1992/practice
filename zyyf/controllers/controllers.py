# -*- coding: utf-8 -*-
from odoo import http

# class Crm(http.Controller):
#     @http.route('/crm/crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm/crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm.listing', {
#             'root': '/crm/crm',
#             'objects': http.request.env['crm.crm'].search([]),
#         })

#     @http.route('/crm/crm/objects/<model("crm.crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm.object', {
#             'object': obj
#         })