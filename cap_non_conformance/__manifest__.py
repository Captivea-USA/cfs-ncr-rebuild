# -*- coding: utf-8 -*-
{
    'name': "CAP Non Conformance",
    'summary': "Non Conformance Flows for failed Quality Checks and Manufacturing Parts",
    'description': "",
    'author': "Captivea",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'quality_control'],

    # always loaded
    'data': [
        'views/ncr_quality.xml',
        'views/ncr_locations.xml',
        'views/ncr_source.xml',
        'views/ncr_reason.xml',
        'views/ncr_severity.xml',
        'views/quality_check.xml',
        'views/ncr_disposition.xml',
        'views/ncr_stage.xml',
        'views/ncr_types.xml',
        'data/ir_sequence_data.xml',
        'data/ncr_data.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
    ],

}
