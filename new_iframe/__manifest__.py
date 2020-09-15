# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Standalone iframe",

    'summary': """
        """,

    'description': """
    """,

    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','web',],

    # always loaded
    'data': [
        'views/iframe_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
