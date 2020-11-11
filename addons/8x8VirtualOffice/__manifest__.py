# -*- coding: utf-8 -*-
{
    'name': "Odoo REST API",

    'summary': """
        Odoo REST API""",

    'description': """
        Odoo REST API
    """,

    'author': "Roko Kokeza",
    'website': "https://8x8.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'developers',
    'version': '0.9',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/authorization.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/virtual_office_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],

    "application": True,
    "installable": True,
    "auto_install": False,

    'external_dependencies': {
        'python': ['pypeg2', 'requests']
    }
}
