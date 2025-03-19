
# Winlock

A simple screen locker application for Windows built with PyQt5.

## Features

- Lock your screen with a customizable hotkey (default: Ctrl+Alt+L)
- Automatic screen locking after a specified idle time
- Optional password protection
- Customizable appearance:
  - Background color or image
  - Clock display (12h/24h format)
  - Font size and color options
- Multi-monitor support
- System tray integration

## Requirements

- Python 3.6+
- Third-party modules:
  - PyQt5: GUI framework
  - pywin32: Windows API integration
  - keyboard: Hotkey support
  - psutil: System monitoring
  - pillow: Image processing
  - cryptography: Password encryption
  - python-dotenv: Configuration management
  - pyautogui: Screen control

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```
pip install PyQt5 pywin32
```

3. Run the application:

```
python main.py
```

## Usage

- **Lock Screen**: Press the configured hotkey (default: Ctrl+Alt+L) to lock your screen.
- **Unlock Screen**: 
  - If password protection is disabled: Press Esc to unlock.
  - If password protection is enabled: Enter your password and press Enter or click the Unlock button.
- **Settings**: Access the settings panel by right-clicking the system tray icon and selecting "Settings".
- **Exit**: Right-click the system tray icon and select "Exit".

## Files

- `main.py`: Entry point of the application
- `screenlocker.py`: Main screen locker functionality
- `settingspanel.py`: Settings panel implementation
- `settingspanel_ui.py`: UI definition for the settings panel
- `utils.py`: Utility functions for the application

## Customization

You can customize the following settings:

- **Hotkey**: Set a custom key combination to lock the screen.
- **Auto-lock**: Enable/disable automatic screen locking after a period of inactivity.
- **Password Protection**: Enable/disable password protection and set a password.
- **Background**: Choose between a solid color or an image background.
- **Clock**: Enable/disable the clock display, choose the format (12h/24h), and customize the font size and color.

## Known Limitations

- Some system key combinations like Ctrl+Alt+Del cannot be completely blocked due to Windows security features.
- The application must be run with administrator privileges to block certain system keys.

## License

This project is released under the MIT License.

## Development Notes

### Known Issues
1. No error handling for invalid hotkey combinations
2. Password hashing needs additional salt mechanism
3. Two-factor authentication not fully implemented
4. Face recognition and fingerprint authentication stubs only
5. Missing webcam detection implementation
6. Missing pattern lock implementation
7. Missing secure clipboard handling during lock screen
8. No rate limiting for failed password attempts
9. Missing secure memory handling for sensitive data
10. No periodic password re-entry requirement

### Features to Implement
1. **Security Enhancements**
   - Secure memory handling for sensitive data
   - Smart card/USB key authentication support
   - Biometric authentication integration
   - Network unlock capability
   - Remote lock/unlock via API
   - Session management

2. **UI Improvements**
   - Customizable unlock animations
   - Touch screen gesture support
   - Custom theme support
   - Accessibility features
   - Multi-language support
   - Screen keyboard for touch devices

3. **System Integration**
   - Better Windows security features integration
   - Group policy support
   - Domain authentication support
   - Event logging system
   - System notifications
   - Power management integration

4. **Additional Features**
   - Scheduled locking/unlocking
   - User session statistics
   - Network presence detection
   - USB device detection
   - Screen recording prevention
   - Emergency unlock procedure

### Exception Handling Needed
1. **File Operations**
   - Settings file corruption
   - Permission issues
   - Disk space issues
   - File lock conflicts

2. **System Integration**
   - OS API failures
   - Registry access errors
   - Group policy conflicts
   - Service communication errors

3. **Hardware Integration**
   - Webcam access errors
   - Biometric device errors
   - Multiple display handling
   - Resolution change handling

4. **Network Related**
   - Authentication service timeout
   - Network disconnection handling
   - API communication errors
   - SSL/TLS errors

5. **Resource Management**
   - Memory allocation errors
   - Thread synchronization
   - Process communication
   - Resource cleanup

### Performance Considerations
1. Memory usage during extended lock periods
2. CPU usage of background monitoring
3. Display handling on multi-monitor setups
4. Resource cleanup during screen changes
5. Impact of background animations
6. Settings file I/O optimization

### Security Audit Needed
1. Password handling procedures
2. Memory sanitization
3. Screen capture prevention
4. Keyboard hook security
5. Authentication mechanism review
6. Encryption implementation review

### Testing Requirements
1. Multi-monitor configurations
2. Different Windows versions
3. Various hardware configurations
4. High-DPI display testing
5. Power state transitions
6. Memory leak detection
7. Long-term stability testing
