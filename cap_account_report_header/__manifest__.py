# -*- coding: utf-8 -*-
{
    "name": "Account Reports Header Customize",
    "version": "15.0.1.0.0",
    "category": "Accounting Reports",
    "license": "AGPL-3",
    "summary": "Account Reports Header Customize",
    "author": "Captivea",
    "website": "http://www.captivea.com",
    "depends": ["cfs_autoexec", "base", "account_reports"],
    "data": ["views/report_financial.xml"],
    "installable": True,
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
}
