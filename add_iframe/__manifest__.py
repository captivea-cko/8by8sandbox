# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Add Iframe",

    'summary': """
        """,

    'description': """
    """,

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',],

    # always loaded
    'data': [
        'views/voip_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],

}
