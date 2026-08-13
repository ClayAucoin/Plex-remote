from http.server import BaseHTTPRequestHandler, HTTPServer
import ctypes

HOST = "0.0.0.0"
PORT = 8765

VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


def play_pause():
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0)


class RemoteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/playpause":
            play_pause()

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Play/Pause sent")

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")


server = HTTPServer((HOST, PORT), RemoteHandler)

print(f"Plex remote listening on port {PORT}")
print(f"Try: http://192.168.1.120:{PORT}/playpause")

server.serve_forever()
