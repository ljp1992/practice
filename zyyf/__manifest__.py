# -*- coding: utf-8 -*-
{
    'name': "zyyf",

    'summary': """
        """,

    'description': """
    """,

    'author': "刘吉平",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # 'data/sequence.xml',
        'views/res_users.xml',
        'views/customer.xml',
        'views/customer_contacter.xml',
        'views/customer_grade.xml',
        'views/customer_type.xml',
        'views/customer_origin.xml',
        'views/customer_state.xml',
        'views/country.xml',
        'views/position.xml',
        'views/customer_follow_record.xml',
        # 'views/product.xml',

        # 'views/supplier.xml',
        # 'views/purchase_order.xml',
        # 'views/sale_order.xml',


        # 'views/task.xml',
        # 'views/contact_customer.xml',
        # 'views/sale_order_remind.xml',
        # 'views/configuration.xml',
        # 'views/task_log.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
}