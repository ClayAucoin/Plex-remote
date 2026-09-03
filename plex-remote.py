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
    "/enter": 0x0D,
    "/left": 0x25,
    "/up": 0x26,
    "/right": 0x27,
    "/down": 0x28,
    "/escape": 0x1B,
}


def press_media_key(vk_code):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


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
    print(f"  {command}")

server.serve_forever()
