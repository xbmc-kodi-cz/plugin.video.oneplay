# -*- coding: utf-8 -*-
import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import uuid

try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath
from datetime import datetime
from urllib.parse import urlencode
import json

plugin_id = 'plugin.video.oneplay'
day_translation = {'1' : 'Pondělí', '2' : 'Úterý', '3' : 'Středa', '4' : 'Čtvrtek', '5' : 'Pátek', '6' : 'Sobota', '0' : 'Neděle'}  
day_translation_short = {'1' : 'Po', '2' : 'Út', '3' : 'St', '4' : 'Čt', '5' : 'Pá', '6' : 'So', '0' : 'Ne'}  

_url = sys.argv[0]
addon = xbmcaddon.Addon()

def check_settings():
    """Kontroluje jestli jsou vyplněné přihlašovací údaje v nastavení doplňku"""    
    if not addon.getSetting('deviceid'):
        addon.setSetting('deviceid', str(uuid.uuid4()))
    if not addon.getSetting('username') or not addon.getSetting('password') or not addon.getSetting('deviceid'):
        display_message('V nastavení je nutné mít vyplněné všechny přihlašovací údaje')
        sys.exit()

def get_url(**kwargs):
    """Formátování URL pro listitem"""
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_kodi_version():
    """Vrací major verzi Kodi"""
    return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

# kod od listenera
def getNumbers(txt):
    newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in txt)
    return [int(i) for i in newstr.split()]

def formatnum(num):
    num = str(num)
    return num if len(num) == 2 else '0' + num

def parsedatetime(_short, _long):
    ix = _short.find(' ')
    lnums = getNumbers(_long)
    snums = getNumbers(_short[:ix])
    year = max(lnums)
    day = min(lnums)
    snums.remove(day)
    day = formatnum(day)
    month = formatnum(min(snums))
    day_formated = '%s.%s.%i' % (day, month, year)
    time_formated = parsetime(_short[ix + 1:])
    return '%s %s' % (day_formated, time_formated)

def parsetime(txt):
    merid = xbmc.getRegion('meridiem')
    h, m = getNumbers(txt)
    if merid.__len__() > 2:
        AM, PM = merid.split('/')
        if txt.endswith(AM) and h == 12:
            h = 0
        elif txt.endswith(PM) and h < 12:
            h += 12
    return '%02d:%02d' % (h, m)

def replace_by_html_entity(string):
    """Nahrazuje problémové znaky html entitami """ 
    return string.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace("'","&apos;").replace('"',"&quot;")

def get_color():
    """Vrací barvu z nastavení"""
    settings_color = addon.getSetting('label_color_live')
    if len(settings_color) > 2 and settings_color.find(']') > 1:
        color = settings_color[1:settings_color.find(']')].replace('COLOR ','')
        return color
    else:
        return ''

def get_label_color(label, color):
    """Nastaví barvu labelu""" 
    return f"[COLOR {color}]{label}[/COLOR]" if color else label

def log_to_file(type, message):
    """Logování do samostatného souboru""" 
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'log.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} {type} > {message}\n")
    except IOError:
        pass

def is_json_string(string):
    """Vrací True pokud má string json formát""" 
    try:
        json.loads(string)
    except ValueError as e:
        return False
    return True    

def get_config_value(setting):
    """Načtení proměnné z nastavení""" 
    addon = xbmcaddon.Addon()
    return addon.getSetting(setting)

def log_message(message):
    """Logování do Kodi.log"""
    xbmc.log('Oneplay > ' + message) 

def display_message(message, message_type = 'error'):
    """Zobrazení notifikace """
    if message_type == 'info':
        message_type = xbmcgui.NOTIFICATION_INFO
    else:
        message_type = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification('Oneplay', message, message_type, 3000)

def display_dialog_yn(heading, message):
    """Zobrazení yes/no dialogu"""
    return xbmcgui.Dialog().yesno(heading, message)  

def display_dialog_pin():
    """Zobrazení dialogu pro zadání PINu"""
    return xbmcgui.Dialog().numeric(type=0, heading='Zadejte PIN', bHiddenInput=True)

class Settings:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_userdata_dir = translatePath(path = self.addon.getAddonInfo('profile'))
        if not os.path.exists(self.addon_userdata_dir):
            os.makedirs(self.addon_userdata_dir)

    @property
    def is_settings_ok(self):
        """Kontroluje nastavení doplňku"""
        if not self.addon.getSetting('username') or not self.addon.getSetting('password'):
            display_message('V nastavení je nutné mít vyplněné přihlašovací údaje')
            return False
        return True

    def _get_path(self, filename):
        """Sestaví cestu k souboru"""
        return os.path.join(self.addon_userdata_dir, filename)

    def save_json_data(self, file_info, data):
        """Uloží json data do souboru"""
        if not self.is_settings_ok:
            return
        filename = self._get_path(file_info['filename'])
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('%s\n' % data)
        except (IOError, OSError) as e:
            display_message(f"Chyba uložení {file_info.get('description', '')}")

    def load_json_data(self, file_info):
        """Načte data ze souboru. Vrací None, pokud soubor neexistuje nebo nejde načíst"""
        if not self.is_settings_ok:
            return None
        filename = self._get_path(file_info['filename'])
        if not os.path.exists(filename):
            return None
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except (IOError, OSError):
            return None

    def reset_json_data(self, file_info):
        """Smaže soubor s json daty"""
        filename = self._get_path(file_info['filename'])
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except (IOError, OSError):
            pass
