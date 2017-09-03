# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError, ValidationError


class Task(models.Model):
    _name = 'task'

    name = fields.Char(string=u'编号')
    date = fields.Date(string=u'任务所属日期')
    create_date = fields.Datetime(string=u'任务创建时间', default=fields.Datetime.now)
    done_date = fields.Datetime(string=u'任务完成时间')
    execute_person = fields.Many2one('res.users', string=u'执行人')
    origin = fields.Selection(selection=[('hand',u'手动获取'),('system',u'系统生成')], string=u'任务来源')
    note = fields.Text(string=u'备注')
    state = fields.Selection(selection=[('to_do', u'待办'), ('done', u'完成')], default='to_do', string=u'状态')
    contact_customers = fields.One2many('contact.customer', 'order_id', string=u'需要联系的客户')
    so_remind_ids = fields.One2many('sale.order.remind', 'order_id', string=u'销售订单')

    @api.one
    def judge_state(self):
        for record in self:
            contact_done = True
            so_remind = True
            for item in record.contact_customers:
                if item.state == 'to_done':
                    contact_done = False
                    break
            for item in record.so_remind_ids:
                if item.state == 'to_done':
                    so_remind = False
                    break
            if contact_done and so_remind:
                record.state = 'done'

    @api.one
    def back_state(self):
        for record in self:
            record.state = 'to_do'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('task.code') or '/'
            print vals['name']
        return super(Task, self).create(vals)

    @api.multi
    def create_task(self, execute_person=None, start_date='', stop_date=''):
        cus_obj = self.env['customer']
        contact_cus_obj = self.env['contact.customer']
        task_obj = self.env['task']
        so_obj = self.env['sale.order']
        so_remind_obj = self.env['sale.order.remind']
        user_obj = self.env['res.users']

        del_so_days = self.env['configuration'].browse(1).so_jiaohuo_remind
        #owners
        owners = {}
        if execute_person:
            execute_person = user_obj.browse(execute_person)
            owners[execute_person] = cus_obj.search([('develop_person','=',execute_person.id)])
        else:
            all_customers = cus_obj.search([])
            for customer in all_customers:
                owner = customer.develop_person
                if owner:
                    if owners.get(owner):
                        owners[owner].append(customer)
                    else:
                        owners[owner] = [customer]

        if start_date == '' and stop_date == '':
            start_date = datetime.datetime.now()
            stop_date = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
            stop_date = datetime.datetime.strptime(stop_date, '%Y-%m-%d %H:%M:%S')
        while (True):
            for (owner,customers) in owners.items():
                day_start = str(start_date)[:10] + ' 00:00:00'
                day_stop = str(start_date)[:10] + ' 23:59:59'
                result = task_obj.search([('state','=','to_do'),
                                          ('date','>=',day_start),
                                          ('date','<=',day_stop)])
                if result:
                    if len(result) == 1:
                        task_id = result[0].id
                    else:
                        info = u'一天中存在多个待办任务'
                        raise ValidationError(_(info))
                else:
                    vals = {'date':str(start_date)[:10],
                            'create_date':fields.Datetime.now,
                            'execute_person':owner.id,
                            'origin':'system',
                            'state':'to_do',}
                    task_id = task_obj.create(vals).id
                # print 'task_id', task_id

                for customer in customers:
                    last_contact_time = customer.last_contact_time
                    if last_contact_time:
                        del_days = customer.del_days
                        if del_days:
                            last_contact_time = datetime.datetime.strptime(last_contact_time, '%Y-%m-%d %H:%M:%S')
                            # print last_contact_time, type(last_contact_time)
                            if last_contact_time + datetime.timedelta(days=del_days) <= start_date:
                                result = contact_cus_obj.search([('state','=','to_do'),('customer_id','=',customer.id)])
                                if not result:
                                    vals = {'order_id':task_id,
                                            'customer_id':customer.id,
                                            'state':'to_do',
                                            'last_contact_time':last_contact_time,}
                                    contact_cus_obj.create(vals)

                sale_orders = so_obj.search([('state','!=','done'),('customer_id.develop_person','=',owner.id)])
                for so in sale_orders:
                    jiaohuo_date = so.jiaohuo_date
                    if jiaohuo_date:
                        jiaohuo_date = datetime.datetime.strptime(jiaohuo_date, '%Y-%m-%d %H:%M:%S')
                        if del_so_days >= 0:
                            if jiaohuo_date - datetime.timedelta(days=del_so_days) <= start_date:
                                result = so_remind_obj.search([('state','=','to_do'),
                                                               ('sale_order_id','=',so.id)])
                                if not result:
                                    vals = {'order_id':task_id,
                                            'sale_order_id':so.id,
                                            'jiaohuo_date':so.jiaohuo_date,
                                            'state':'to_do',}
                                    so_remind_obj.create(vals)

            start_date += datetime.timedelta(days=1)
            if start_date >= stop_date:
                break
        return

class TaskLog(models.Model):
    _name = 'task.log'

    name = fields.Char(default=u'任务日志')
    origin = fields.Selection(selection=[('system',u'系统'),('hand',u'手动')], string=u'任务来源')
    success = fields.Boolean(string=u'创建成功')
    create_time = fields.Datetime(string=u'创建时间')
    error = fields.Text(string=u'错误信息')

class ContactCustomer(models.Model):
    _name = 'contact.customer'
    _rec_name = 'customer_id'

    order_id = fields.Many2one('task', string=u'任务', ondelete='cascade')
    customer_id = fields.Many2one('customer', string=u'客户')
    state = fields.Selection(selection=[('to_do',u'待办'),('done',u'完成')], default='to_do', string=u'状态')
    note = fields.Text(string=u'备注')
    last_contact_time = fields.Datetime(string=u'上次联系时间')
    grade_id = fields.Many2one('grade')
    del_day = fields.Integer(string=u'间隔天数')

    # last_contact_time = fields.Datetime(string=u'上次联系时间', compute="_get_last_contact_time", store=True)

    #已联系客户
    # @api.multi
    def contact_done(self):
        # print self
        for record in self:
            record.state = 'done'

    @api.multi
    def view_customer(self):
        return {
            'name': _(u'客户'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.customer_id.id,
            'view_id': self.env.ref('crm_my.task_customer_form').id,
        }

    @api.one
    def task_done(self):
        for record in self:
            record.customer_id.last_contact_time = datetime.datetime.now()
            record.state = 'done'
            # record.order_id.judge_state()

    # @api.depends('customer_id')
    # def _get_last_contact_time(self):
    #     for record in self:
    #         record.last_contact_time = record.customer_id.last_contact_time

    # @api.multi
    # @api.depends('customer_id')
    # def _get_last_contact_time(self):
    #     print '_get_last_contact_time'
    #     for record in self:
    #         record.last_contact_time = record.customer_id.last_contact_time

class SaleOrderRemind(models.Model):
    _name = 'sale.order.remind'

    order_id = fields.Many2one('task', string=u'任务', ondelete='cascade')
    sale_order_id = fields.Many2one('sale.order', string=u'销售订单')
    customer_id = fields.Many2one('customer', related='sale_order_id.customer_id', string=u'客户', store=False)
    jiaohuo_date = fields.Date(string=u'交货日期')
    state = fields.Selection(selection=[('to_do', u'待办'), ('done', u'完成')], default='to_do', string=u'状态')

    @api.multi
    def view_so(self):
        return {
            'name': _(u'销售订单'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }

    @api.one
    def task_done(self):
        for record in self:
            record.sale_order_id.jiaohuo_date = datetime.datetime.now()
            record.state = 'done'
            # record.order_id.judge_state()