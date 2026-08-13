Set shell = CreateObject("WScript.Shell")

shell.Run "curl.exe -s http://192.168.1.120:8765/playpause", 0, True

Set shell = Nothing

' http://192.168.1.120:8765/volumeup
' http://192.168.1.120:8765/volumedown
' http://192.168.1.120:8765/mute
' http://192.168.1.120:8765/next
' http://192.168.1.120:8765/previous