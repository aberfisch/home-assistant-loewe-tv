# Changelog – Loewe TV Home Assistant Integration

Alle wesentlichen Änderungen werden hier fortlaufend dokumentiert. Geplant und implementiert werden getrennt ausgewiesen. Versionsnummern für lokale Test-ZIPs sind nicht automatisch GitHub-Releases.

## [Unreleased]

### Geplant
- Dynamische DVB-C-Senderlistenabfrage und Zuordnung der 197 Sender
- Korrekte Anzeige des aktuellen Senders anhand des Loewe-Locators
- Zuverlässiger Wechsel zwischen TV, Radio und HDMI
- Diagnoseprotokolle für SOAP-Antworten und Fehler
- HACS-kompatible Veröffentlichung und Versionierung

### Bekannte Probleme (Rückmeldung vom Loewe Connect 48, SL320, Firmware 5.4.6.0)
- Senderliste erscheint nicht in Home Assistant
- Aktueller Sender wird als interne Kennung statt als Name angezeigt
- Auswahl von HDMI und Radio löst keinen Quellenwechsel aus
- Power, Lautstärke und Mute funktionieren laut Gerätetest zuverlässig

## Frühere lokale Teststände (nicht als GitHub-Release verifiziert)

### 1.0.2 – Quellenwechsel-Test
- Test-ZIP für alternative Quellensteuerung bereitgestellt
- Funktion am Gerät noch nicht bestätigt

### 1.0.1 – Senderlisten-Test
- Test-ZIP für Senderauswertung und Senderauswahl bereitgestellt
- Gerätetest: Keine Senderliste sichtbar; interne Kennung wird angezeigt

---
Dokumentationsgrundlage: Loewe Remote API 1.0.47. Änderungen werden künftig mit Version, Datum, Implementierungsstatus und Teststatus ergänzt.
