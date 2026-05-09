import os
import sys
import platform
import subprocess
from pathlib import Path

def setup_windows():
    import winreg
    python_exe = sys.executable
    script_path = str(Path("main.py").resolve())
    
    # We use a special 'CommandStore' trick to make it look more official
    # and try to bypass the 'Show more options' clutter where possible.
    command = f'"{python_exe}" "{script_path}" --send-file "%1"'
    
    # Use AXO icon if available, otherwise python icon
    icon_path = sys.executable
    
    # Registry paths for high-priority visibility
    keys = [
        r"*\shell\AXO",                 # Files
        r"Directory\shell\AXO",         # Folders
        r"Directory\Background\shell\AXO", # Background
        r"Drive\shell\AXO"              # Whole Drives
    ]
    
    try:
        for key_path in keys:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{key_path}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "Share with AXO")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
                winreg.SetValueEx(key, "Position", 0, winreg.REG_SZ, "Top") # Try to force to top
                
                with winreg.CreateKey(key, "command") as cmd_key:
                    val = command.replace("%1", "%V") if "Background" in key_path else command
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, val)
        
        print("[+] Windows 11 High-Priority integration applied.")
        print("[!] Note: To appear at the absolute top of the Modern Menu, AXO requires a signed Sparse Package (MSIX).")
    except Exception as e:
        print(f"[-] Windows integration failed: {e}")

def setup_linux():
    # Dolphin (KDE)
    kio_path = Path.home() / ".local/share/kio/servicemenus"
    kio_path.mkdir(parents=True, exist_ok=True)
    
    desktop_file = kio_path / "axo_share.desktop"
    content = f"""[Desktop Entry]
Type=Service
ServiceTypes=KonqPopupMenu/Plugin
MimeType=all/all;
Actions=axoShare;
X-KDE-Priority=TopLevel

[Desktop Action axoShare]
Name=Share with AXO
Icon=network-transmit
Exec={sys.executable} {Path("main.py").resolve()} --send-file %f
"""
    desktop_file.write_text(content)
    
    # Nautilus (GNOME) - Using simple scripts folder as it's the most reliable without extra deps
    nautilus_path = Path.home() / ".local/share/nautilus/scripts"
    nautilus_path.mkdir(parents=True, exist_ok=True)
    script_file = nautilus_path / "Share with AXO"
    script_content = f"#!/bin/bash\n{sys.executable} {Path('main.py').resolve()} --send-file \"$1\""
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print("[+] Linux context menu integrated (Dolphin & Nautilus).")

def setup_macos():
    # macOS uses Services (Automator) or Finder Sync Extensions.
    # The simplest "one-script" way is to create a Quick Action (.workflow)
    # This is complex to do purely via Python without pyobjc, but we can 
    # provide instructions or a basic Automator wrapper.
    print("[!] macOS: Please use Automator to create a 'Quick Action' that runs:")
    print(f"    {sys.executable} {Path('main.py').resolve()} --send-file \"$1\"")

def integrate_all():
    system = platform.system()
    if system == "Windows":
        setup_windows()
    elif system == "Linux":
        setup_linux()
    elif system == "Darwin":
        setup_macos()
    else:
        print(f"[-] Unsupported system for native integration: {system}")

if __name__ == "__main__":
    integrate_all()
