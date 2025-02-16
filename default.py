# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC entry point
# ------------------------------------------------------------

import os
import sys
import time
import xml.etree.ElementTree as ET
import xbmc
import xbmcaddon
import xbmcvfs

from platformcode import config, logger

logger.info("init...")

librerias = xbmc.translatePath(os.path.join(config.get_runtime_path(), 'lib'))
sys.path.insert(0, librerias)
os.environ['TMPDIR'] = config.get_temp_file('')

from platformcode import launcher

def check_plugin_video_kod():
    """Controlla se l'addon 'plugin.video.kod' è installato ed eventualmente avvisa l'utente"""
    addon_id = 'plugin.video.kod'
    try:
        addon = xbmcaddon.Addon(addon_id)
        if addon.isEnabled():
            xbmc.executebuiltin('Notification(Attenzione, plugin.video.kod verrà sostituito con plugin.video.s4me, 5000)')
            xbmc.log("L'addon plugin.video.kod è installato. Verrà sostituito con plugin.video.s4me.", xbmc.LOGINFO)
        else:
            xbmc.log("L'addon plugin.video.kod non è abilitato. Nessuna sostituzione necessaria.", xbmc.LOGINFO)
    except RuntimeError:
        xbmc.log("L'addon plugin.video.kod non è installato.", xbmc.LOGINFO)

def enable_addon(addon_id):
    """Abilita l'addon specificato se non è già attivo e aggiorna la lista degli addon"""
    check_plugin_video_kod()

    try:
        addon = xbmcaddon.Addon(addon_id)
        if addon.isEnabled():
            xbmc.log(f"L'addon {addon_id} è già abilitato.", xbmc.LOGINFO)
        else:
            addon.setEnabled(True)
            xbmc.log(f"L'addon {addon_id} è stato abilitato.", xbmc.LOGINFO)
        
        xbmc.executebuiltin("UpdateAddonRepos")
        xbmc.executebuiltin("UpdateLocalAddons")
        time.sleep(2)  # Attendi per permettere il refresh
        xbmc.log("Il refresh degli addon è stato completato.", xbmc.LOGINFO)
    except RuntimeError:
        xbmc.log(f"L'addon {addon_id} non è installato.", xbmc.LOGWARNING)

def modify_source_url(old_url, new_url):
    """Modifica il file sources.xml per aggiornare la sorgente URL"""
    sources_path = xbmc.translatePath(os.path.join('special://profile/', 'sources.xml'))

    if not xbmcvfs.exists(sources_path):
        xbmc.log("Il file sources.xml non esiste.", xbmc.LOGWARNING)
        return

    try:
        tree = ET.parse(sources_path)
        root = tree.getroot()
        source_modified = False

        for source in root.findall(".//source"):
            path_element = source.find("path")
            if path_element is not None and path_element.text == old_url:
                path_element.text = new_url
                source_modified = True
                xbmc.log(f"Sorgente URL cambiata da {old_url} a {new_url}.", xbmc.LOGINFO)
                break

        if source_modified:
            tree.write(sources_path)
            xbmc.log("File sources.xml aggiornato con il nuovo URL.", xbmc.LOGINFO)
        else:
            xbmc.log(f"Nessuna sorgente trovata con URL {old_url}.", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"Errore durante la modifica di sources.xml: {str(e)}", xbmc.LOGERROR)

# Esegui il controllo degli addon e modifica la sorgente URL prima di avviare Kodi
enable_addon("plugin.video.s4me")
modify_source_url('http://kodiondemand.github.io/repo/', 'https://stream4me.github.io/repo/')

# Avvio del launcher
if len(sys.argv) < 3 or sys.argv[2] == "":
    launcher.start()

launcher.run()
