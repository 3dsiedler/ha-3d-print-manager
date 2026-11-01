# Changelog

Alle wichtigen Änderungen an diesem Projekt. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Geändert
- Foto-Upload-Karte: Drückst du im Wareneingang „Neu“ (oder wurde gebucht), verschwindet das angezeigte Typenschild-Foto und der Status wird zurückgesetzt.

### Hinzugefügt
- Wareneingang: Vorschläge aus der Open Filament Database (openfilamentdatabase.org, MIT-Lizenz) per EAN oder Hersteller + Material + Farbe/Farbcode. Das Material (PLA, PETG, …) muss immer übereinstimmen. Übernommen werden Hersteller, Material, Farbe, Farbcode, EAN und Rollengröße erst nach deiner Auswahl. Die Daten werden einmalig geladen und wöchentlich erneuert.
- Spulenwarnung: Meldung auf Handy und per Alexa (im Zeitfenster), wenn die aktive Spule unter 10 % und unter 5 % fällt sowie bei „Spule leer“ (unter 15 g). Die Meldung schlägt gleich eine identische Spule aus dem Lager vor (gleicher Hersteller, gleiches Material, gleiche Farbe – nie ein anderes Material oder anderer Hersteller) (mind. 30 % Rest, einstellbar; die mit dem geringsten Rest zuerst). Alle Schwellen in den Einstellungen änderbar.
- Lichtsteuerung 3D-Druck: schaltet das Licht (frei wählbarer Schalter) zur eingestellten Uhrzeit aus; läuft dann schon ein Druck (oder startet nachts einer), sofort; sonst bleibt es nach einem frischen Upload noch die eingestellte Nachlaufzeit an. Taster „Licht an“ im Reiter Drucker schaltet es für eine einstellbare Dauer wieder ein. Alles in den Einstellungen anpassbar.
- Karte „Nachtplanung“ im Reiter Drucker: schlägt aus den offenen Dateien den längsten Druck vor, der mit 15 min Reserve ins Nachtfenster passt und dessen Spule stimmt (ein Druck pro Nacht); Start und Ende der Nacht in den Einstellungen.

## [0.1.1-beta] – 2026-10-31

### Hinzugefügt
- Mehrere Rollen pro Buchung können eigene Chargen haben: im Feld Charge durch Komma trennen, Rolle 1 bekommt die erste Charge usw. (eine einzelne Charge gilt für alle Rollen). Die Foto-Auswertung hängt bei Anzahl > 1 weitere Chargen automatisch an.
- Foto-Auswertung ergänzt statt zu überschreiben: Karton-Foto (SKU, Barcode, Packungsgröße) und Rollen-Foto (Charge, Farbe, Gewicht) lassen sich nacheinander auswerten; leere Erkennungswerte löschen vorhandene Felder nicht mehr.
- Foto-Auswertung: SKU wird als Hersteller-Bestellnr. übernommen, Charge nur bei eindeutiger Beschriftung (Lot/Batch/Charge), alphanumerischer Barcode (z. B. Sunlu X002…), Packungsgröße (3KG = 3×1 kg, 0.5KG*2 = 2×500 g).
- Wareneingang: Feld „Hersteller-Bestellnr.“ – wird beim Einbuchen in das FilaMan-Zusatzfeld `herstbestellnr` der Spule geschrieben (Zusatzfeld vom Typ Text muss für Spulen angelegt sein)
- Wareneingang: Auswahl „Neue Sorte anlegen über“ – „In HA anlegen (wie bisher)“ oder „FilaManDB in FilaMan (Test)“. Im Testmodus legt HA nichts an, sondern zeigt die Anleitung, die Sorte in FilaMan per „Load from FilaManDB“ anzulegen; danach findet erneutes Einbuchen sie.

### Behoben
- Foto-Auswertung: Fehler bei rein numerischem Barcode („int object is not subscriptable“); Material, Farbcode und Farbe werden nur noch übernommen, wenn sie auf dem Foto stehen (kein Raten mehr)
- Händlerliste im Wareneingang wird nach einem Neuladen der YAML-Helfer automatisch wieder gefüllt
- Dashboard: Markdown-Karten verloren Zeilenumbrüche (Lagerbestand: Typenliste in der Überschrift, zweiter Lagerort fehlte)
- Leere Textfelder (Kalkulation, Wareneingang) zeigten „unknown“ – werden jetzt beim Start geleert

### Neu
- Meldung bei Druckende (fertig/Fehler/abgebrochen) per Handy-Push und Alexa-Durchsage mit einstellbarem Zeitfenster; Antippen der Handy-Meldung öffnet das Dashboard (Companion-App)
- Wareneingang: bis zu 3 passende bekannte Sorten als Vorschlag (Übernahme erst nach Auswahl, Werte bleiben änderbar), Abweichungsanzeige zur bekannten Sorte
- Wareneingang: neue Sorte bzw. neuer Hersteller wird nur nach ausdrücklicher Bestätigung (Schalter) angelegt, sonst Rückfrage
- Wareneingang: Händler (an der Spule im Kommentar vermerkt), optionale Charge/Lot-Nr., Rollengewicht wird als Anfangsgewicht der Spule gespeichert
- Einstellung „Bevorzugte Händler“ (Standard Amazon, Polymaker, Sunlu): Auswahlliste im Wareneingang und Vorschlag in der Bestellliste
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
