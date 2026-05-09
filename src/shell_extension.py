import pythoncom
import win32gui
import win32con
from win32com.shell import shell, shellcon
import win32api
import os
import sys
import uuid

# CLSID for the AXO Shell Extension
# You should generate a unique one for your app
CLSID = "{A76E5B4C-1234-5678-90AB-CDEF12345678}"

class AXOExplorerCommand:
    _reg_progid_ = "AXO.ShellExtension"
    _reg_desc_ = "AXO Modern Context Menu Extension"
    _reg_clsid_ = CLSID
    
    # These are the IExplorerCommand methods
    # Note: pywin32 might not have native IExplorerCommand wrappers, 
    # so we often have to use IContextMenu as a fallback or 
    # a custom COM implementation.
    
    def GetTitle(self, items, name):
        return "Share with AXO"
        
    def GetIcon(self, items, icon):
        # Point to the AXO icon or python exe
        return sys.executable + ",0"
        
    def GetState(self, items, okWrite):
        return 0 # ECS_ENABLED
        
    def Invoke(self, items, bindCtx):
        # Get the selected item path
        if items:
            count = items.GetCount()
            for i in range(count):
                item = items.GetItemAt(i)
                path = item.GetDisplayName(shellcon.SIGDN_FILESYSPATH)
                # Launch AXO with the file path
                subprocess.Popen([sys.executable, "main.py", "--send-file", path])
        return 0 # S_OK

# For Windows 11 Primary Menu, the most reliable "Pure Python" way 
# without a C++ shim is to use the 'ExplorerCommandHandler' registry key 
# combined with a Sparse Package.

def register_com_server():
    import win32com.server.register
    win32com.server.register.UseCommandLine(AXOExplorerCommand)

if __name__ == "__main__":
    register_com_server()
