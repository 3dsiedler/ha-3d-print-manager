# Changelog

Alle wichtigen Änderungen an diesem Projekt. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Behoben
- Dashboard: Markdown-Karten verloren Zeilenumbrüche (Lagerbestand: Typenliste in der Überschrift, zweiter Lagerort fehlte)
- Leere Textfelder (Kalkulation, Wareneingang) zeigten „unknown“ – werden jetzt beim Start geleert

### Neu
- Meldung bei Druckende (fertig/Fehler/abgebrochen) per Handy-Push und Alexa-Durchsage mit einstellbarem Zeitfenster; Antippen der Handy-Meldung öffnet das Dashboard (Companion-App)
- Screenshots im README

## [0.1.0-beta] – 2026-10-31

Erste öffentliche Beta (getestet mit Sovol SV08, Klipper, Moonraker, FilaMan über die Spoolman-kompatible API, OrcaSlicer 2.4).

### Neu
- Package `3d_print_manager.yaml` mit Druckeranbindung an einer Stelle (Abschnitt 1) und Einstellungen im Dashboard
- Drucker: Fortschrittsbalken mit Endzeit, laufende Druckkosten (Filament/Strom), OK-/Fehldruck-Buchung mit Umbuchen
- Letzte 10 Drucke und Druckwarteschlange („Noch zu drucken“) mit Vorschaubildern
- Filamentprüfung je Datei: exaktes Material, Farbe (falls im Slicer gesetzt), Rollenwechsel im Druck nur gleicher Hersteller, Spulenvorschläge aus Plätzen und Lager
- G-Codes verwerfen/zurückholen (Ordner `verworfen` auf dem Drucker)
- Auftragskalkulation (Material, Strom, Maschine, Rüsten, Nacharbeit, Konstruktion, Aufschlag), geplante Aufträge, Bestellliste mit Mindestbestand und Lieferantenvorschlag
- Lernender Erfahrungswert „kWh pro Druckstunde“
- Wareneingang nach Spoolman: manuell, per Vorlage oder per Foto vom Typenschild (AI Task), Barcode-Wiedererkennung
- Upload-Karte `pm-foto-upload-card` (Drag & Drop / Kamera, automatische Auswertung)
- Lagerübersicht: Plätze am Drucker mit Überbelegungs-Warnung, Bestand je Lagerort
- Dashboard mit den Reitern Drucker, Aufträge, Wareneingang, Lager, Einstellungen (inkl. Verbindungstest)
