Set shell = CreateObject("WScript.Shell")

shell.Run "curl.exe -s http://192.168.1.120:8765/left", 0, True

Set shell = Nothing