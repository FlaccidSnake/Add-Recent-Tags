# -*- coding: utf-8 -*-
"""
Anki Add-on: Add Recent Tags
Adds a menu to quickly access recently used tags.
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""
from . import add_recent_tags
from .config_dialog import show_config_dialog
from aqt import mw

# Register config action
mw.addonManager.setConfigAction(__name__, show_config_dialog)