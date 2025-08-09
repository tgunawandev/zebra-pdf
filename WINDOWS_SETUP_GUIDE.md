# Windows Setup Guide for Zebra Print Control System

This guide helps you set up the Zebra Print Control System on Windows without Docker Desktop.

## Prerequisites

### 1. Python Installation
- Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- During installation, make sure to check "Add Python to PATH"
- Verify installation by opening Command Prompt and running:
  ```cmd
  python --version
  ```

### 2. Git (Optional but recommended)
- Download and install Git from [git-scm.com](https://git-scm.com/downloads)
- This allows you to clone the repository and receive updates

### 3. cURL (For API testing)
- Windows 10 version 1803+ includes cURL by default
- For older versions, download from [curl.se](https://curl.se/windows/)
- Verify by running: `curl --version`

### 4. Cloudflared (For tunnel functionality)
- Download from [Cloudflare GitHub releases](https://github.com/cloudflare/cloudflared/releases)
- Place the executable in a folder that's in your PATH
- Verify by running: `cloudflared --version`

## Installation Steps

### Step 1: Download the Project
If you have Git:
```cmd
git clone <repository-url>
cd zebra-pdf
```

Or download and extract the ZIP file to a folder.

### Step 2: Install Python Dependencies
Open Command Prompt in the project folder and run:
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Connect Your Zebra Printer
- Connect your Zebra printer via USB
- Install the printer drivers from Zebra's website
- Make sure the printer is detected in Windows Device Manager

### Step 4: Configure the System
Run the setup wizard:
```cmd
zebra.bat setup
```

Follow the on-screen prompts to configure:
- Printer settings
- Network configuration
- Cloudflare tunnel (optional)

## Using the System

### Basic Commands

Start the system:
```cmd
zebra.bat start
```

Check system status:
```cmd
zebra.bat status
```

Stop the system:
```cmd
zebra.bat stop
```

Access interactive control panel:
```cmd
zebra.bat shell
```

### Configuration Commands

Run setup wizard:
```cmd
zebra.bat setup
```

Configure custom domain:
```cmd
zebra.bat domain
```

Setup Cloudflare authentication:
```cmd
zebra.bat auth
```

### Testing Commands

Check system health:
```cmd
zebra.bat health
```

Test printer connection:
```cmd
zebra.bat printer
```

Test API endpoints:
```cmd
zebra.bat api
```

Run system tests:
```cmd
zebra.bat test
```

### Information Commands

Show help:
```cmd
zebra.bat help
```

Show version information:
```cmd
zebra.bat version
```

Check installation requirements:
```cmd
zebra.bat install
```

## Troubleshooting

### Python Not Found
If you get "Python is not installed or not in PATH":
1. Reinstall Python and check "Add Python to PATH"
2. Or manually add Python to your PATH environment variable
3. Restart Command Prompt after making changes

### Permission Issues
If you get permission errors:
1. Run Command Prompt as Administrator
2. Or ensure you have write permissions to the project folder

### Port 5000 Already in Use
If port 5000 is already in use:
1. Check what's using the port: `netstat -ano | findstr :5000`
2. Stop the conflicting service or configure a different port
3. Edit the configuration files to use a different port

### Printer Not Detected
If the printer is not detected:
1. Ensure the printer is connected and powered on
2. Install the latest drivers from Zebra's website
3. Check Windows Device Manager for printer status
4. Try a different USB port or cable

### Cloudflare Tunnel Issues
If tunnel setup fails:
1. Ensure cloudflared is installed and in PATH
2. Run `cloudflared tunnel login` manually
3. Check your Cloudflare account permissions
4. Verify your domain configuration

## File Structure

```
zebra-pdf/
├── zebra.bat                 # Main management script
├── zebra_control_v2.py       # Main Python application
├── requirements.txt          # Python dependencies
├── zebra_print/             # Python package
├── tests/                   # Test files
└── WINDOWS_SETUP_GUIDE.md   # This guide
```

## Support

- Check the system logs in the `logs/` directory (if it exists)
- Run `zebra.bat health` to diagnose issues
- Use `zebra.bat printer` to check printer connectivity
- Use `zebra.bat api` to test API endpoints

## Next Steps

After successful installation:
1. Test printing with the interactive control panel: `zebra.bat shell`
2. Configure your custom domain for external access: `zebra.bat domain`
3. Set up monitoring and logging as needed
4. Integrate with your existing systems using the API

The system provides a REST API at `http://localhost:5000` for integration with other applications.