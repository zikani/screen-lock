import os
import json
import sys
import time
import hashlib
import platform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDesktopWidget

# Constants
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_SETTINGS = {
    "hotkey": "Ctrl+Alt+L",
    "enable_timer": False,
    "idle_timeout": 5,
    "enable_password": False,
    "password": "",  # Changed default to empty string for security
    "password_hash": "",  # Added for storing hashed password
    "bg_color": "#000000",
    "bg_image": "",  # Path to background image
    "enable_clock": True,
    "clock_24h": False,
    "clock_size": 40,
    "clock_color": "#FFFFFF",
    "debug_mode": False,  # Debug mode for force closing the lock screen
    "autostart": False,
    "system_tray": False,
    "minimize_to_tray": False,
    "auth_method": "Password",
    "hash_passwords": True,  # Changed default to True for security
    "two_factor": False,
    "two_factor_method": "Email",
    "max_attempts": 3,
    "lockout_duration": 5,
    "recovery_email": "",
    "use_recovery_questions": False,
    "recovery_questions": [],  # Added to store recovery questions
    "recovery_answers": [],    # Added to store hashed answers
    "background_type": "Color",
    "show_clock": True,
    "clock_format": "12 Hour",
    "lock_on_startup": False,  # Added new option
    "custom_message": "",      # Added for custom lock screen message
    "last_locked": 0           # Track when screen was last locked
}

def validate_settings(settings):
    """Validate the loaded settings."""
    if not isinstance(settings, dict):
        return False
    
    # First check that all required keys exist with correct types
    # We don't simply check equality of types because we want to allow
    # compatible numeric types (int/float)
    for key, default_value in DEFAULT_SETTINGS.items():
        if key not in settings:
            return False
        
        # Special handling for numeric types
        if isinstance(default_value, (int, float)):
            if not isinstance(settings[key], (int, float)):
                return False
        # Special handling for lists
        elif isinstance(default_value, list):
            if not isinstance(settings[key], list):
                return False
        # All other types must match exactly
        elif not isinstance(settings[key], type(default_value)):
            return False
    
    return True

def load_settings(default=False):
    """
    Load settings from the settings file.
    Args:
        default (bool): If True, return default settings without loading from file
    """
    try:
        if default:
            return DEFAULT_SETTINGS.copy()

        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                if not validate_settings(settings):
                    print("Settings file is corrupted. Using default settings.")
                    return DEFAULT_SETTINGS.copy()
                
                # Ensure all default settings are present
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                
                # Handle password migration if needed
                if settings["hash_passwords"] and settings["password"] and not settings["password_hash"]:
                    settings["password_hash"] = hash_password(settings["password"])
                    settings["password"] = ""  # Clear plaintext password
                    
                return settings
        else:
            # Create the settings file with default values if it doesn't exist
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    except FileNotFoundError:
        print(f"Settings file not found. Creating default settings: {SETTINGS_FILE}")
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    except json.JSONDecodeError:
        print(f"Error decoding settings file. Using default settings: {SETTINGS_FILE}")
        # Backup corrupted file for potential recovery
        backup_corrupted_settings()
        return DEFAULT_SETTINGS.copy()
    except OSError as e:
        print(f"OS error occurred while loading settings: {e}")
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Unexpected error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def backup_corrupted_settings():
    """Create a backup of corrupted settings file."""
    if os.path.exists(SETTINGS_FILE):
        backup_file = f"{SETTINGS_FILE}.bak.{int(time.time())}"
        try:
            with open(SETTINGS_FILE, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            print(f"Corrupted settings file backed up to: {backup_file}")
        except Exception as e:
            print(f"Failed to backup corrupted settings: {e}")

def save_settings(settings):
    """Save settings to the settings file with basic error handling."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        # Write settings directly to file
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk
            
        return True

    except Exception as e:
        print(f"Error saving settings: {e}")
        raise

def get_idle_time():
    """Get the idle time in seconds."""
    try:
        if is_windows():
            import win32api
            import win32con
            return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
        elif is_linux():
            # For Linux, we would need to implement this differently
            # This is a placeholder
            print("Idle time detection not implemented for Linux.")
            return 0
        elif is_mac():
            # For macOS, we would need to implement this differently
            # This is a placeholder
            print("Idle time detection not implemented for macOS.")
            return 0
        else:
            print("Idle time detection not supported on this OS.")
            return 0
    except ImportError:
        print("Required modules for idle time detection not available.")
        return 0
    except Exception as e:
        print(f"Error getting idle time: {e}")
        return 0

def parse_hotkey(hotkey_str):
    """Parse a hotkey string into modifier and key."""
    modifiers = 0
    key = 0

    # Map common modifier strings to Qt modifiers
    modifier_map = {
        "Ctrl": Qt.ControlModifier,
        "Alt": Qt.AltModifier,
        "Shift": Qt.ShiftModifier,
        "Meta": Qt.MetaModifier,
        "Win": Qt.MetaModifier  # Windows key is usually mapped to Meta
    }

    parts = hotkey_str.split("+")

    # Last part is the key
    key_str = parts[-1].strip()

    # Try to map the key to a Qt key
    key_attr = f"Key_{key_str}"
    if hasattr(Qt, key_attr):
        key = getattr(Qt, key_attr)
    else:
        # If it's a single character, use its ASCII value
        if len(key_str) == 1:
            key = ord(key_str.upper())

    # Process modifiers
    for part in parts[:-1]:
        part = part.strip()
        if part in modifier_map:
            modifiers |= modifier_map[part]

    return modifiers, key

def lock_workstation():
    """Lock the workstation based on OS."""
    if is_windows():
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception as e:
            print(f"Error locking Windows workstation: {e}")
            return False
    elif is_linux():
        try:
            # Common Linux lock commands
            commands = [
                "dbus-send --type=method_call --dest=org.gnome.ScreenSaver " +
                "/org/gnome/ScreenSaver org.gnome.ScreenSaver.Lock",
                "loginctl lock-session",
                "gnome-screensaver-command --lock",
                "xdg-screensaver lock",
                "cinnamon-screensaver-command --lock",
                "mate-screensaver-command --lock"
            ]
            
            for cmd in commands:
                try:
                    if os.system(cmd) == 0:
                        return True
                except:
                    continue
            
            print("Failed to lock Linux workstation with available commands.")
            return False
        except Exception as e:
            print(f"Error locking Linux workstation: {e}")
            return False
    elif is_mac():
        try:
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
            return True
        except Exception as e:
            print(f"Error locking macOS workstation: {e}")
            return False
    else:
        print("Locking not supported on this OS.")
        return False

def fullscreen_on_all_monitors():
    """Get a list of geometries for all monitors to create fullscreen windows."""
    desktop = QDesktopWidget()
    geometries = []

    for i in range(desktop.screenCount()):
        geometries.append(desktop.screenGeometry(i))

    return geometries

def is_windows():
    """Check if the current OS is Windows."""
    return platform.system() == "Windows"

def is_linux():
    """Check if the current OS is Linux."""
    return platform.system() == "Linux"

def is_mac():
    """Check if the current OS is macOS."""
    return platform.system() == "Darwin"

def setup_autostart(enable=True):
    """Set up or remove autostart for the application."""
    app_name = "WindowsScreenLocker"
    app_path = f'"{os.path.abspath(sys.argv[0])}"'  # Quote the path
    
    if is_windows():
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"Error setting up Windows autostart: {e}")
            return False
    elif is_linux():
        # Create autostart file for Linux
        autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        autostart_file = os.path.join(autostart_dir, f"{app_name}.desktop")
        
        try:
            if enable:
                os.makedirs(autostart_dir, exist_ok=True)
                with open(autostart_file, 'w') as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={app_path}
Terminal=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
""")
            else:
                if os.path.exists(autostart_file):
                    os.remove(autostart_file)
            return True
        except Exception as e:
            print(f"Error setting up Linux autostart: {e}")
            return False
    elif is_mac():
        # Create launch agent for macOS
        launchagent_dir = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents")
        launchagent_file = os.path.join(launchagent_dir, f"com.user.{app_name}.plist")
        
        try:
            if enable:
                os.makedirs(launchagent_dir, exist_ok=True)
                with open(launchagent_file, 'w') as f:
                    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.{app_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>""")
                os.system(f"launchctl load {launchagent_file}")
            else:
                if os.path.exists(launchagent_file):
                    os.system(f"launchctl unload {launchagent_file}")
                    os.remove(launchagent_file)
            return True
        except Exception as e:
            print(f"Error setting up macOS autostart: {e}")
            return False
    
    return False

def hash_password(password):
    """Hash the password using a secure hashing algorithm with salt."""
    # Use a unique salt based on the username to prevent rainbow table attacks
    try:
        salt = hashlib.sha256(os.getlogin().encode()).hexdigest()[:16]
        hashed = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            10000  # Number of iterations
        )
        return salt + hashlib.sha256(hashed).hexdigest()
    except Exception as e:
        print(f"Error hashing password: {e}")
        # Fallback to simple hash if something goes wrong
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Verify a password against its stored hash."""
    try:
        if len(stored_hash) > 16:  # We expect at least 16 chars of salt
            salt = stored_hash[:16]
            hashed = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt.encode(), 
                10000
            )
            computed_hash = salt + hashlib.sha256(hashed).hexdigest()
            return computed_hash == stored_hash
        else:
            # Legacy verification (simple hash)
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def encrypt_data(data, key):
    """Encrypt sensitive data."""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Generate a key from the password
        salt = b'screen_locker_salt'  # A fixed salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        
        # Encrypt the data
        f = Fernet(derived_key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except ImportError:
        print("Cryptography module not available. Data not encrypted.")
        return data
    except Exception as e:
        print(f"Error encrypting data: {e}")
        return data

def decrypt_data(encrypted_data, key):
    """Decrypt sensitive data."""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Generate the same key from the password
        salt = b'screen_locker_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        
        # Decrypt the data
        f = Fernet(derived_key)
        decrypted_data = f.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode()
    except ImportError:
        print("Cryptography module not available. Data not decrypted.")
        return encrypted_data
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return ""

def is_elevated():
    """Check if the application is running with elevated privileges."""
    try:
        if is_windows():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif is_linux() or is_mac():
            return os.geteuid() == 0
        return False
    except Exception as e:
        print(f"Error checking for elevated privileges: {e}")
        return False

def kill_windows_lock_screen():
    """Kill the Windows lock screen process if running."""
    if is_windows():
        try:
            import subprocess
            subprocess.run(['taskkill', '/F', '/IM', 'LockApp.exe'], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            print(f"Error killing Windows lock screen: {e}")
            return False
    return False

def set_as_default_lock_screen(enable=True):
    """Set this application as the default Windows lock screen."""
    if not is_windows():
        return False, "This feature is only available on Windows"
        
    if not is_elevated():
        return False, "Administrator privileges required"
        
    try:
        import winreg
        app_path = f'"{os.path.abspath(sys.argv[0])}"'
        
        # Kill the Windows lock screen process first
        kill_windows_lock_screen()
        
        # Registry keys for lock screen integration
        key_paths = [
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        ]
        
        for key_path in key_paths:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                              winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                if enable:
                    if "Winlogon" in key_path:
                        winreg.SetValueEx(key, "CustomLockUI", 0, winreg.REG_SZ, app_path)
                    if "System" in key_path:
                        # Disable the default lock screen
                        winreg.SetValueEx(key, "DisableLockWorkstation", 0, winreg.REG_DWORD, 0)
                else:
                    try:
                        if "Winlogon" in key_path:
                            winreg.DeleteValue(key, "CustomLockUI")
                        if "System" in key_path:
                            winreg.DeleteValue(key, "DisableLockWorkstation")
                    except FileNotFoundError:
                        pass
                        
        # Force update group policy
        if is_elevated():
            os.system("gpupdate /force")
            
        return True, "Successfully updated lock screen settings"
    except Exception as e:
        return False, f"Failed to set as default lock screen: {str(e)}"

def request_admin_privileges():
    """Request administrator privileges by relaunching the app."""
    if is_windows():
        try:
            import ctypes, sys
            if not is_elevated():
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
            return True
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            return False
    return False