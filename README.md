# web-fusee-launcher
Fusee Launcher im Browser! Geforkt von [web-fusee-launcher](https://github.com/atlas44/web-fusee-launcher) von atlas44.

Deutscher Fork von [Niklas080208](https://github.com/Niklas080208) mit deutscher Übersetzung und Cyan-Hintergrund.

# Beschreibung
Dies ist ein Web-Port von [fusee-launcher](https://github.com/reswitched/fusee-launcher) nach JavaScript unter Verwendung von WebUSB.

Es funktioniert auf Linux, Android (ohne Root), macOS und ChromeOS. Es funktioniert NICHT unter Windows, da die WebUSB Windows-Implementierung das Senden des erforderlichen USB-Pakets nicht erlaubt.

# Ausprobieren
Online verfügbar unter: https://webrcm.github.io

Der ursprüngliche Quellcode befindet sich bei: [atlas44's Demo](https://atlas44.s3-us-west-2.amazonaws.com/web-fusee-launcher/index.html).

# Linux-Info
Wenn du einen Zugriff verweigert-Fehler erhältst, erstelle eine Datei unter `/etc/udev/rules.d/50-switch.rules` mit folgendem Inhalt:

```
SUBSYSTEM=="usb", ATTR{idVendor}=="0955", MODE="0664", GROUP="plugdev"
```