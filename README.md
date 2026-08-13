# Plex Remote Control

A simple LAN-based remote control that allows a Stream Deck on one Windows PC to control Plex playback on another Windows PC.

The project uses a lightweight Python HTTP server on the Plex computer and `curl.exe` commands from the controlling computer.

## How It Works

```text
Stream Deck
    ↓
VBS Script
    ↓
curl.exe
    ↓
Local Network
    ↓
Python HTTP Server
    ↓
Windows Media Key
    ↓
Plex
```

The Python server listens for HTTP requests on port `8765`. When it receives a request, it generates the corresponding Windows media key.

For example:

```text
http://192.168.1.120:8765/playpause
```

sends the Windows **Play/Pause** media key on the Plex computer.

## Requirements

### Plex Computer

- Windows
- Python 3
- Plex
- Network connection to the controlling PC

### Controlling PC

- Windows
- Stream Deck
- `curl.exe` (included with modern versions of Windows)
- Network connection to the Plex computer

## Python Server

The Plex computer runs `plex_remote.py`:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import ctypes

HOST = "0.0.0.0"
PORT = 8765

KEYEVENTF_KEYUP = 0x0002

MEDIA_KEYS = {
    "/playpause": 0xB3,
    "/stop": 0xB2,
    "/next": 0xB0,
    "/previous": 0xB1,
    "/volumeup": 0xAF,
    "/volumedown": 0xAE,
    "/mute": 0xAD,
}


def press_media_key(vk_code):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(
        vk_code, 0, KEYEVENTF_KEYUP, 0
    )


class RemoteHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in MEDIA_KEYS:
            press_media_key(MEDIA_KEYS[self.path])

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            action = self.path.lstrip("/")
            self.wfile.write(f"{action} sent".encode())

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Unknown command")

    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")


server = HTTPServer((HOST, PORT), RemoteHandler)

print(f"Remote control listening on port {PORT}")
print("Available commands:")

for command in MEDIA_KEYS:
    print(f"  http://192.168.1.120:{PORT}{command}")

server.serve_forever()
```

Start the server with:

```cmd
python plex_remote.py
```

The server listens on:

```text
0.0.0.0:8765
```

This allows other computers on the LAN to connect to it.

## Available Commands

| Endpoint      | Action              |
| ------------- | ------------------- |
| `/playpause`  | Play/Pause          |
| `/stop`       | Stop                |
| `/next`       | Next track/item     |
| `/previous`   | Previous track/item |
| `/volumeup`   | Volume Up           |
| `/volumedown` | Volume Down         |
| `/mute`       | Mute/Unmute         |

For a Plex computer at `192.168.1.120`, Play/Pause can be triggered with:

```text
http://192.168.1.120:8765/playpause
```

## Windows Firewall

The Plex computer must allow incoming TCP connections on port `8765`.

Open PowerShell as Administrator and run:

```powershell
New-NetFirewallRule `
  -DisplayName "Plex Remote 8765" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8765 `
  -Action Allow `
  -Profile Private
```

The computer's LAN connection should be configured as a **Private** Windows network.

Check it with:

```powershell
Get-NetConnectionProfile
```

If necessary, change the appropriate interface to Private:

```powershell
Set-NetConnectionProfile -InterfaceIndex <INDEX> -NetworkCategory Private
```

Do not change VPN or other unrelated network interfaces just to run the remote.

## Testing the Server

On the Plex computer:

```cmd
netstat -ano | findstr :8765
```

A working server should show something similar to:

```text
TCP    0.0.0.0:8765    0.0.0.0:0    LISTENING
```

From the controlling PC, test connectivity with:

```powershell
Test-NetConnection 192.168.1.120 -Port 8765
```

A successful connection will show:

```text
TcpTestSucceeded : True
```

You can also test Play/Pause directly from a browser:

```text
http://192.168.1.120:8765/playpause
```

## Using curl

The controlling PC sends commands using the Windows `curl.exe` executable.

Example:

```cmd
curl.exe -s http://192.168.1.120:8765/playpause
```

The server should respond:

```text
playpause sent
```

and Plex should toggle between playing and paused.

## Stream Deck

A small VBS script can execute the `curl.exe` command without displaying a Command Prompt window.

### Play/Pause

Create:

```text
playpause.vbs
```

with:

```vbscript
Set shell = CreateObject("WScript.Shell")
shell.Run "curl.exe -s http://192.168.1.120:8765/playpause", 0, True
Set shell = Nothing
```

In Stream Deck:

1. Add a **System → Open** action.
2. Select `playpause.vbs` as the file to open.
3. Assign an appropriate Play/Pause icon.

Pressing the Stream Deck button will now toggle Plex playback on the remote computer.

Additional VBS scripts can use the other endpoints:

```text
/stop
/next
/previous
/volumeup
/volumedown
/mute
```

For example:

```vbscript
Set shell = CreateObject("WScript.Shell")
shell.Run "curl.exe -s http://192.168.1.120:8765/mute", 0, True
Set shell = Nothing
```

## Starting the Server Automatically

The Python server can be started automatically when the Plex computer logs into Windows using **Task Scheduler**.

Create a task with:

### General

- **Name:** Plex Remote Server
- **Run only when user is logged on**
- Configure the task for the installed version of Windows.

### Trigger

```text
At log on
```

Using **At log on** instead of **At startup** allows the Python process to run inside the interactive Windows session where it can generate media-key presses.

### Action

Set **Program/script** to the full path of the Python executable.

The exact Python executable can be found with:

```powershell
python -c "import sys; print(sys.executable)"
```

Set **Add arguments** to:

```text
"C:\path\to\plex_remote.py"
```

Set **Start in** to the directory containing the script:

```text
C:\path\to
```

Do not include quotation marks around the **Start in** directory.

### Settings

Recommended options:

- Allow task to be run on demand
- Run task as soon as possible after a scheduled start is missed
- If the task is already running: **Do not start a new instance**

If the laptop should remain controllable while running on battery, disable the Task Scheduler conditions that prevent or stop the task when the computer switches to battery power.

## Network Address

The Stream Deck scripts depend on the Plex computer being available at the configured IP address.

For example:

```text
192.168.1.120
```

It is recommended to create a **DHCP reservation** in the router so the Plex computer continues receiving the same IP address.

If its IP address changes, the URLs in the VBS scripts must also be changed.

## Important Notes

The media controls use Windows media keys rather than the Plex API.

Because of this:

- Play/Pause, Next, Previous, and Stop operate on the active Windows media session.
- Volume Up, Volume Down, and Mute control Windows system volume.
- If another media application becomes the active media session, media commands may control that application instead of Plex.

## Security

This server is intended for use on a trusted local network.

It currently:

- Uses plain HTTP.
- Has no authentication.
- Listens on all network interfaces.
- Executes only the predefined media commands.

Do **not** expose port `8765` to the Internet or create a router port-forward for it.

For normal home use, keep the server accessible only from the local network.

## Troubleshooting

### Works locally but not from another PC

Verify the server is listening:

```cmd
netstat -ano | findstr :8765
```

Then check the port from the controlling PC:

```powershell
Test-NetConnection 192.168.1.120 -Port 8765
```

If ping succeeds but the TCP connection fails, check:

- Windows Firewall
- Windows network profile
- VPN LAN-blocking settings
- Whether Python is actually listening on port `8765`

### Browser works but Stream Deck does not

Test `curl.exe` manually:

```cmd
curl.exe -s http://192.168.1.120:8765/playpause
```

If that works, test the VBS file by double-clicking it before assigning it to Stream Deck.

### Task Scheduler says Running but the server does not respond

Check:

```cmd
netstat -ano | findstr :8765
```

If nothing is listening, verify:

- The Python executable path
- The `plex_remote.py` path
- The Task Scheduler **Start in** directory
- That another copy of the server is not already using port `8765`

## Future Improvements

Possible additions include:

- Single reusable VBS script with command arguments
- Restrict access to specific LAN IP addresses
- Authentication token
- Plex-specific controls using the Plex API
- Launch/close Plex remotely
- Lock, restart, or shut down the laptop
- Laptop status endpoint
- Stream Deck feedback showing playback state
- Automatic discovery instead of a hard-coded IP address

Although this project started as a Plex remote, the HTTP server can be expanded into a general-purpose LAN remote for controlling other functions on the Windows computer.
