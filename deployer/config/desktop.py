# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Deployer",
			"color": "blue",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Deployer")
		}
	]
