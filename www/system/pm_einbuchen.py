"""Rollen in FilaMan/Spoolman einbuchen (Schema der Open Filament Database).
Feld 'Material' im Wareneingang = Sorte (z. B. PLA+ 2.0). FilaMan-Material = Klasse (PLA), Name = Sorte + Farbe."""
import sys, json, base64, re, urllib.request as u
API = sys.argv[1].rstrip("/") + "/"
def r(m, p, body=None):
    data = json.dumps(body).encode() if body is not None else None
    q = u.Request(API + p, data=data, method=m, headers={"Content-Type": "application/json"})
    return json.load(u.urlopen(q, timeout=15))
def norm(s):
    s = (s or "").lower().replace("+", " plus ").replace("plus", " plus ")
    return " ".join(re.sub(r"[^a-z0-9.]+", " ", s).split())
def klasse(s):
    w = norm(s).split()
    for k in ("PETG", "PLA", "ABS", "ASA", "TPU", "PET", "PC", "PA12", "PA6", "PA"):
        for x in w:
            if x == k.lower() or (x.startswith(k.lower()) and not x[len(k):len(k) + 1].isalpha()):
                return k
    return (s.split() or [s])[0].upper()
DE_EN = {"weiß": "White", "weiss": "White", "ws": "White", "grau": "Grey", "gray": "Grey", "schwarz": "Black", "sw": "Black",
         "gelb": "Yellow", "grün": "Green", "gruen": "Green", "blau": "Blue", "rot": "Red", "rosa": "Pink", "braun": "Brown",
         "lila": "Purple", "violett": "Purple", "silber": "Silver", "kaltweiß": "Cold White", "kaltweiss": "Cold White"}
DICHTE = {"pla": 1.24, "petg": 1.27, "pet": 1.27, "abs": 1.04, "asa": 1.07, "tpu": 1.21, "pa": 1.14, "pc": 1.2}
try:
    d = json.loads(base64.b64decode(sys.argv[2]).decode())
    herst, mat, farbe = d["hersteller"].strip(), d["material"].strip(), d["farbe"].strip()
    hexw = (d.get("hex") or "").strip().lstrip("#").upper()
    gew = float(d["gewicht"])
    anz = int(float(d.get("anzahl") or 1))
    ean = (d.get("ean") or "").strip()
    preis = float(d.get("preis") or 0)
    ort = d.get("ort") or "Lager"
    haendler = (d.get("haendler") or "").strip()
    charge = (d.get("charge") or "").strip()
    chargen = [c.strip() for c in charge.replace(";", ",").replace("\n", ",").split(",") if c.strip()]
    bestellnr = (d.get("bestellnr") or "").strip()
    neu_ok = bool(d.get("neu_ok"))
    fdb = bool(d.get("filamandb"))
    if not herst or not mat or not farbe:
        raise ValueError("Hersteller, Sorte und Farbe angeben")
    fil = r("GET", "filament")
    f = None
    farbe = DE_EN.get(farbe.lower(), farbe)
    sorte = mat
    kl = klasse(mat)
    name_neu = (sorte + " " + farbe).strip()
    kompakt = lambda s: norm(s).replace(" ", "")
    if ean:
        f = next((x for x in fil if (x.get("article_number") or "") == ean), None)
    if f is None:
        for x in fil:
            v = ((x.get("vendor") or {}).get("name") or "")
            if norm(v) != norm(herst) or abs(float(x.get("weight") or 0) - gew) >= 1:
                continue
            if kompakt(x.get("name")) == kompakt(name_neu):
                f = x
                break
    neu = False
    if f is None:
        vorh = next((v for v in r("GET", "vendor") if norm(v["name"]) == norm(herst)), None)
        if fdb:
            print(json.dumps({"ok": False, "rueckfrage": True, "text": "Diese Sorte gibt es noch nicht: " + herst + " " + name_neu + " (" + str(int(gew)) + " g). Modus FilaManDB: In FilaMan unter Filamente neu anlegen, Hersteller waehlen, Load from FilaManDB, Sorte auswaehlen, speichern. Danach hier erneut Einbuchen - die Sorte wird dann gefunden. Alternativ den Modus auf In HA anlegen stellen."}))
            raise SystemExit
        if not neu_ok:
            print(json.dumps({"ok": False, "rueckfrage": True, "text": "Diese Sorte gibt es noch nicht: " + herst + " " + name_neu + " (" + str(int(gew)) + " g)" + ("" if vorh else " - auch der Hersteller " + herst + " ist neu") + ". Wenn das stimmt: im Wareneingang den Schalter Neue Sorte anlegen erlauben einschalten und erneut Einbuchen. Sonst oben einen Vorschlag waehlen."}))
            raise SystemExit
        ven = vorh or r("POST", "vendor", {"name": herst})
        body = {"name": name_neu, "vendor_id": ven["id"], "material": kl, "weight": gew, "diameter": 1.75, "density": DICHTE.get(kl.lower(), 1.24)}
        if hexw:
            body["color_hex"] = hexw
        if ean:
            body["article_number"] = ean
        if preis:
            body["price"] = preis
        f = r("POST", "filament", body)
        neu = True
    elif ean and not f.get("article_number"):
        r("PATCH", "filament/" + str(f["id"]), {"article_number": ean})
    for i in range(anz):
        sb = {"filament_id": f["id"], "location": ort, "initial_weight": gew}
        if preis:
            sb["price"] = preis
        if haendler:
            sb["comment"] = "Haendler: " + haendler
        if chargen:
            c1 = chargen[i] if len(chargen) > 1 and i < len(chargen) else (chargen[0] if len(chargen) == 1 else "")
            if c1:
                sb["lot_nr"] = c1
        if bestellnr:
            sb["extra"] = {"herstbestellnr": json.dumps(bestellnr)}
        r("POST", "spool", sb)
    txt = str(anz) + "x " + herst + " " + (f.get("name") or name_neu) + " (" + str(int(gew)) + " g) in " + ort + " eingebucht"
    txt += (" - neue Filamentsorte #" + str(f["id"]) + " angelegt") if neu else (" - Sorte #" + str(f["id"]))
    print(json.dumps({"ok": True, "text": txt}))
except SystemExit:
    pass
except Exception as e:
    print(json.dumps({"ok": False, "text": "Fehler beim Einbuchen: " + str(e)}))
