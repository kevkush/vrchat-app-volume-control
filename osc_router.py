
# ===============================================================
# VRChat OSC → Per-Application Volume Controller
# v0.2
# 
# Listens for pre-mapped OSC parameters from VRChat and maps them
# to per app volume control
#
# USAGE:
# create an actionless float parameter in VRC controlled w/ radial
# map the same parameter name to a process in this script
# volume control go brrrr
#
# prerequisites: python-osc, pycaw, comtypes
#
# ===============================================================

import time
import re
import threading
from datetime import datetime

import comtypes
from pythonosc import dispatcher, osc_server
from pycaw.pycaw import AudioUtilities

# ===============================================================
# Configuration
# ===============================================================

# name your VRCHAT parameters the same as this, add to this for more app control (ex given as spotify)
PARAM_MAP = {
    "ChromeVolume": {"process": "chrome.exe"},
    "VRCVolume": {"process": "vrchat.exe"},
#   "SpotifyVolume": {"process": "spotify.exe"},
}

# If using VRCFury, parameters are renamed, use this to remove the prefix
STRIP_VRCFURY_PREFIX = True
VRCFURY_PREFIX_PATTERN = r"^VF\d+_"

# usually don't gotta change these
VRCHAT_PORT = 9001
SEND_INTERVAL = 0.1  # seconds

# ===============================================================
# Configuration END
# ===============================================================

# logging
def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

# the volume controller
class VolumeController:
    def __init__(self):
        self.latest_values = {}
        self.last_applied_values = {}
        self.session_cache = {}
        self.process_seen = {}
        
    # check/detect/cache audio sessions for proper per-app control    
    def _get_session(self, process_name: str):
        session = self.session_cache.get(process_name)

        if session and session.Process and session.Process.is_running():
            if session.Process.name().lower() == process_name.lower():
                return session
            else:
                self.session_cache.pop(process_name, None)

        for s in AudioUtilities.GetAllSessions():
            if s.Process and s.Process.name().lower() == process_name.lower():
                self.session_cache[process_name] = s

                if not self.process_seen.get(process_name):
                    log(f"Process detected: {process_name}")
                    self.process_seen[process_name] = True

                return s

        if self.process_seen.get(process_name):
            log(f"Process closed: {process_name}")
            self.process_seen[process_name] = False

        return None

    def set_volume(self, process_name: str, volume_percent: int) -> None:
        session = self._get_session(process_name)
        if not session:
            return

        session.SimpleAudioVolume.SetMasterVolume(
            volume_percent / 100.0,
            None
        )

    # OSC decoding
    def handle_osc(self, address: str, *args):
        param = address.split("/")[-1]

        if STRIP_VRCFURY_PREFIX:
            param = re.sub(VRCFURY_PREFIX_PATTERN, "", param)

        if param not in PARAM_MAP or not args:
            return

        value = int(round(args[0] * 100))
        self.latest_values[param] = value

    
    # set that volume when it changes, baby
    def apply_loop(self):
        comtypes.CoInitialize()

        try:
            while True:
                for param, value in list(self.latest_values.items()):
                    if self.last_applied_values.get(param) == value:
                        continue

                    process_name = PARAM_MAP[param]["process"]
                    self.set_volume(process_name, value)

                    self.last_applied_values[param] = value
                    log(f"{process_name} → {value}%")

                time.sleep(SEND_INTERVAL)

        finally:
            comtypes.CoUninitialize()

# our main little workerbee
def main():
    log("VRChat OSC → Volume Controller")
    log(f"Listening on UDP port {VRCHAT_PORT}")

    controller = VolumeController()

    disp = dispatcher.Dispatcher()
    disp.map("/*", controller.handle_osc)

    server = osc_server.ThreadingOSCUDPServer(
        ("127.0.0.1", VRCHAT_PORT),
        disp
    )

    threading.Thread(
        target=controller.apply_loop,
        daemon=True
    ).start()

    server.serve_forever()

if __name__ == "__main__":

    main()

