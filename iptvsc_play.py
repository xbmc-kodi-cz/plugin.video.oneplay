# -*- coding: utf-8 -*-
import xbmc
from resources.lib.utils import plugin_id
from resources.lib.channels import Channels

channels_list = Channels().get_channels_list('name', visible_filter=False)
channel = xbmc.getInfoLabel('ListItem.ChannelName')
if channel and channel in channels_list:
    xbmc.executebuiltin(f"PlayMedia(plugin://{plugin_id}?action=iptsc_play_stream&id={channels_list[channel]['id']}&fromstart=True)")