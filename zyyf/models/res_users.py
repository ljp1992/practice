# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResUsersr(models.Model):
    _inherit = 'res.users'

    #根据permission值 给用户赋权限
    @api.multi
    def change_permission(self, vals):
        permission = vals.get('permission')
        if permission:
            if permission == 'salesman':
                res_groups = self.env['ir.model.data'].xmlid_to_object('zyyf.salesman')
                if res_groups and len(res_groups) == 1:
                    vals['groups_id'] = [[6, False, [res_groups[0].id, 1, 7, 8]]]
            elif permission == 'manager':
                res_groups = self.env['ir.model.data'].xmlid_to_object('zyyf.manager')
                if res_groups and len(res_groups) == 1:
                    vals['groups_id'] = [[6, False, [res_groups[0].id, 1, 7, 8]]]
        return vals

    @api.multi
    def write(self, vals):
        vals = self.change_permission(vals)
        return super(ResUsersr, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self.change_permission(vals)
        return super(ResUsersr, self).create(vals)

    @api.one
    def set_unuseable(self):
        for record in self:
            record.useable = False

    @api.one
    def set_useable(self):
        for record in self:
            record.useable = True