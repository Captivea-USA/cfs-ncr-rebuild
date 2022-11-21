# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Team on Project and Tasks',
    'price': 21.0,
    'version': '2.1.6',
    'depends': [
        "cfs_autoexec", 
            'project',
    ],
    'category' : 'Projects',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Project Team on Project and Task Form.""",
    'description': """
Project Teams
Project Team on Project
project team
team management
team manager
projects team
project team
team member
team user
team project
team task
task team
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_team_odoo/664',#'https://youtu.be/vl44ZUhSpRY',
    'data':[
        'security/ir.model.access.csv',
        'views/project_team_view.xml',
        'views/project_view.xml',
       
    ],
    'installable' : True,
    'application' : False,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
