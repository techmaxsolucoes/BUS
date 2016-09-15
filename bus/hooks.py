# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "bus"
app_title = "Bus"
app_publisher = "MaxMorais"
app_description = "Supersimple Async Methods and interservice communication bus with autodiscovery and cache"
app_icon = "octicon octicon-database"
app_color = "grey"
app_email = "max.morais.dmm@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bus/css/bus.css"
# app_include_js = "/assets/bus/js/bus.js"

# include js, css files in header of web template
# web_include_css = "/assets/bus/css/bus.css"
# web_include_js = "/assets/bus/js/bus.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "bus.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "bus.install.before_install"
# after_install = "bus.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bus.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bus.tasks.all"
# 	],
# 	"daily": [
# 		"bus.tasks.daily"
# 	],
# 	"hourly": [
# 		"bus.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bus.tasks.weekly"
# 	]
# 	"monthly": [
# 		"bus.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "bus.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bus.event.get_events"
# }

