If WScript.Arguments.Count = 0 Then
    WScript.Quit
End If

Set shell = CreateObject("WScript.Shell")

LaptopIP = "192.168.1.180"
Port = "8765"

Action = WScript.Arguments(0)

URL = "http://" & LaptopIP & ":" & Port & "/" & Action

shell.Run "curl.exe -s """ & URL & """", 0, True

Set shell = Nothing