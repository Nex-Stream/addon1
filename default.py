# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC entry point
# ------------------------------------------------------------

import os
import sys
import xbmc

# Funzioni che su Kodi 19 sono state spostate in xbmcvfs
try:
    import xbmcvfs
    xbmc.translatePath = xbmcvfs.translatePath
    xbmc.validatePath = xbmcvfs.validatePath
    xbmc.makeLegalFilename = xbmcvfs.makeLegalFilename
except:
    pass
from platformcode import config, logger

logger.info("init...")

librerias = xbmc.translatePath(os.path.join(config.get_runtime_path(), 'lib'))
sys.path.insert(0, librerias)
os.environ['TMPDIR'] = config.get_temp_file('')

from platformcode import launcher

# Aggiungi il nuovo codice prima di avviare l'applicazione Kodi
def check_plugin_video_kod():
    # Controlla se l'addon 'plugin.video.kod' è installato
    addon_id = 'plugin.video.kod'
    addon = xbmcaddon.Addon(addon_id)

    if addon.isEnabled():
        # Se l'addon è abilitato, mostra un messaggio di avviso
        xbmc.executebuiltin('Notification(Attenzione, plugin.video.kod verrà sostituito con stream4me, 5000)')
        xbmc.log("L'addon plugin.video.kod è installato. Verrà sostituito con stream4me.")
    else:
        xbmc.log("L'addon plugin.video.kod non è abilitato. Nessuna sostituzione necessaria.")

def enable_addon(addon_id):
    # Verifica se l'addon "plugin.video.kod" è già installato prima di fare qualsiasi altra operazione
    check_plugin_video_kod()

    # Crea l'oggetto addon utilizzando l'ID
    addon = xbmcaddon.Addon(addon_id)

    # Verifica se l'addon è abilitato
    if addon.isEnabled():
        xbmc.log(f"L'addon {addon_id} è già abilitato.")
    else:
        xbmc.log(f"L'addon {addon_id} non è abilitato.")

    # Abilita l'addon se non è abilitato
    if not addon.isEnabled():
        addon.setEnabled(True)
        xbmc.log(f"L'addon {addon_id} è stato abilitato.")

    # Ricarica la lista degli addon installati (effettua il refresh)
    xbmc.log("Ricaricando gli addon installati...")

    # Usa la funzione di Kodi per ricaricare gli addon
    xbmc.executebuiltin("UpdateAddonRepos")
    xbmc.executebuiltin("UpdateLocalAddons")

    # Diamo un po' di tempo per completare il refresh
    time.sleep(2)
    xbmc.log("Il refresh degli addon è stato completato.")

    # Modifica la sorgente URL
    old_url = 'http://kodiondemand.github.io/repo/'  # URL da modificare
    new_url = 'https://stream4me.github.io/repo/'  # Nuovo URL
    modify_source_url(old_url, new_url)

def modify_source_url(old_url, new_url):
    # Ottieni il percorso del file sources.xml
    sources_path = xbmc.translatePath(os.path.join('special://profile/', 'sources.xml'))

    # Verifica se il file sources.xml esiste
    if not os.path.exists(sources_path):
        xbmc.log("Il file sources.xml non esiste.")
        return

    # Analizza il file XML
    tree = ET.parse(sources_path)
    root = tree.getroot()

    # Trova la sorgente che ha il path uguale a old_url
    source_modified = False
    for source in root.findall('source'):
        path = source.get('path')
        if path == old_url:
            # Modifica solo la URL della sorgente
            source.set('path', new_url)
            source_modified = True
            xbmc.log(f"Sorgente URL cambiata da {old_url} a {new_url}.")
            break

    if not source_modified:
        xbmc.log(f"Sorgente con URL {old_url} non trovata.")

    # Salva le modifiche al file sources.xml
    if source_modified:
        tree.write(sources_path)
        xbmc.log(f"File sources.xml aggiornato.")

# Ora, esegui il resto del codice Kodi come da tua configurazione
if sys.argv[2] == "":
    launcher.start()

launcher.run()
