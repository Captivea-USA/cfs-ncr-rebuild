# -*- coding: utf-8 -*-
{
    "name": "CFS Website Footer",
    "author": "Commonwealth Fusion Systems",
    "website": "http://cfs.energy",
    "category": "Website/Website",
    "version": "15.0",
    "license": "OEEL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "summary": "CFS owned modifications to Portal",
    "description": "CFS owned modifications to Portal",
    "cloc_exclude": ["./**/*"],  # exclude all files in a module recursively
    "images": ["static/description/icon.png"],
    "depends": ["cfs_autoexec", "website"],
    "data": ["views/footer_top.xml", "views/footer_bottom.xml"],
}
