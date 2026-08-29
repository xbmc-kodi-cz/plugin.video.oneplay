# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin

from resources.lib.utils import get_url

def list_settings(label):
    """Menu Nastavení Oneplay"""
    handle = int(sys.argv[1])
    xbmcplugin.setPluginCategory(handle, label)
    menu_items = [
        ('Kanály', 'manage_channels', True),
        ('Profily', 'list_profiles', True),
        ('Účty', 'list_accounts', True),
        ('Nastavení doplňku', 'addon_settings', False)
    ]
    for item_label, action, is_folder in menu_items:
        list_item = xbmcgui.ListItem(label=item_label)
        url = get_url(action=action, label=item_label)
        xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(handle)
