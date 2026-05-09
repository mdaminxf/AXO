# AXO Modern Windows 11 Integration

This module provides a professional, top-level context menu integration for Windows 11.

## Components
1. **`src/shell_extension.py`**: The COM server that handles the right-click command.
2. **`AppxManifest.xml`**: The manifest that grants AXO the "Package Identity" required for the modern Windows 11 menu.
3. **`install_axo_menu.py`**: The unified installer/unregister script.

## Requirements
- **Developer Mode**: Must be ENABLED in Windows Settings (Privacy & security > For developers).
- **Administrator Privileges**: Required for package registration.

## Installation
Run the installer from an Administrator terminal:
```powershell
python install_axo_menu.py
```
*Note: You may need to restart Explorer (Task Manager > Restart Explorer) to see the changes.*

## Removal
To completely remove the integration:
```powershell
python install_axo_menu.py --unregister
```

## How it works
AXO uses an **IExplorerCommand** COM server combined with a **Sparse Package**. This is the official Microsoft-recommended way for Win32 apps to appear in the primary modern context menu on Windows 11 without being forced into "Show more options".
