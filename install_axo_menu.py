import os
import sys
import subprocess
import winreg
import ctypes
from pathlib import Path

# Constants
CLSID = "{A76E5B4C-1234-5678-90AB-CDEF12345678}"
PROGID = "AXO.ShellExtension"
PACKAGE_NAME = "AXO.Collaboration.System"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_com():
    print("[*] Registering COM Server...")
    try:
        # Register the COM server class
        cmd = [sys.executable, "src/shell_extension.py", "--register"]
        subprocess.run(cmd, check=True)
        
        # Additional Registry for IExplorerCommand
        # This tells Windows where the command handler is
        keys = [r"*", r"Directory", r"Directory\Background"]
        for k in keys:
            path = rf"Software\Classes\{k}\shell\AXO"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
                winreg.SetValueEx(key, "ExplorerCommandHandler", 0, winreg.REG_SZ, CLSID)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, sys.executable)
        
        print("[+] COM Server registered.")
    except Exception as e:
        print(f"[-] COM registration failed: {e}")

def register_sparse_package():
    print("[*] Registering Windows 11 Sparse Package (Identity)...")
    # PowerShell command to register the manifest as a sparse package
    # -ExternalLocation must be the root folder of our app
    manifest_path = str(Path("AppxManifest.xml").resolve())
    external_location = str(Path(".").resolve())
    
    ps_cmd = f'Add-AppxPackage -Path "{manifest_path}" -Register -ExternalLocation "{external_location}"'
    
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], check=True)
        print("[+] Sparse Package registered. AXO now has Identity.")
    except Exception as e:
        print(f"[-] Sparse Package registration failed: {e}")
        print("[!] Note: This requires Developer Mode enabled in Windows Settings.")

def unregister_all():
    print("[*] Unregistering AXO Shell Extension...")
    
    # 1. Unregister Sparse Package
    ps_cmd = f'Get-AppxPackage -Name "{PACKAGE_NAME}" | Remove-AppxPackage'
    subprocess.run(["powershell", "-Command", ps_cmd], stderr=subprocess.DEVNULL)
    
    # 2. Unregister COM
    cmd = [sys.executable, "src/shell_extension.py", "--unregister"]
    subprocess.run(cmd, stderr=subprocess.DEVNULL)
    
    # 3. Clean Registry
    keys = [r"*", r"Directory", r"Directory\Background"]
    for k in keys:
        try:
            path = rf"Software\Classes\{k}\shell\AXO"
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except:
            pass
            
    print("[+] AXO Shell Extension removed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--unregister":
        unregister_all()
    else:
        if not is_admin():
            print("[!] Requesting Administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        else:
            register_com()
            register_sparse_package()
            print("\n[SUCCESS] AXO Modern Context Menu is now active!")
            print("[!] You may need to restart explorer.exe to see changes.")
