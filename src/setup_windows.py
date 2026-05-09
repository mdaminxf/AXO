import winreg
import sys
import os
from pathlib import Path

def add_context_menu():
    # Path to the python executable and the main.py script
    python_exe = sys.executable
    script_path = str(Path("main.py").resolve())
    
    # Command to run when clicked
    command = f'"{python_exe}" "{script_path}"'
    
    # Registry paths
    keys = [
        r"*\shell\MultiOSCollab",       # Files
        r"Directory\shell\MultiOSCollab" # Folders
    ]
    
    try:
        for key_path in keys:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "Share with Multi-OS")
                # Add an optional sub-label or icon here if desired
                
                with winreg.CreateKey(key, "command") as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
        
        print("[+] Context menu added for files and folders.")
    except Exception as e:
        print(f"[-] Failed to add context menu: {e}")
        print("Note: You may need to run this script as Administrator.")

if __name__ == "__main__":
    add_context_menu()
