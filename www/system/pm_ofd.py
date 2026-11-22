import sys, os, json, csv, re, time, base64, urllib.request
BASE = os.environ.get("OFD_BASE", "https://api.openfilamentdatabase.org/csv/")
DIR = sys.argv[1]
MODE = sys.argv[2]
DATEIEN = ["brands", "materials", "filaments", "variants", "sizes"]
csv.field_size_limit(10**8)

def pfad(n):
    return os.path.join(DIR, "ofd_" + n + ".csv")

def aktuell():
    try:
        return all(os.path.exists(pfad(n)) and time.time() - os.path.getmtime(pfad(n)) < 7 * 86400 for n in DATEIEN)
    except Exception:
        return False

def laden():
    os.makedirs(DIR, exist_ok=True)
    for n in DATEIEN:
        daten = urllib.request.urlopen(urllib.request.Request(BASE + n + ".csv", headers={"User-Agent": "ha-3d-print-manager"}), timeout=60).read()
        with open(pfad(n) + ".tmp", "wb") as f:
            f.write(daten)
        os.replace(pfad(n) + ".tmp", pfad(n))

def lies(n):
    with open(pfad(n), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def nm(s):
    s = (s or "").lower().replace("+", " plus ")
    return re.sub(r"[^a-z0-9]+", "", s)

def hexrgb(h):
    h = (h or "").strip().lstrip("#")
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return None

def ean_norm(s):
    return re.sub(r"\D", "", s or "").lstrip("0")

if MODE == "update":
    laden()
    print("ok")
    raise SystemExit

LAST = os.path.join(DIR, "ofd_letzte_treffer.json")

if MODE == "waehlen":
    label = json.loads(base64.b64decode(sys.argv[3]).decode()).get("label", "")
    try:
        for t in json.load(open(LAST)):
            if t["label"] == label:
                print(json.dumps(t, ensure_ascii=False))
                raise SystemExit
    except FileNotFoundError:
        pass
    print("{}")
    raise SystemExit

# MODE == "suchen": ean hersteller material(=Sorte) farbe hex gewicht
q = json.loads(base64.b64decode(sys.argv[3]).decode())
ean, herst, mat, farbe, hexw, gew = [str(q.get(k, "")) for k in ("ean", "hersteller", "material", "farbe", "hex", "gewicht")]
DE_EN = {"weiß": "White", "weiss": "White", "ws": "White", "grau": "Grey", "gray": "Grey", "schwarz": "Black", "sw": "Black",
         "gelb": "Yellow", "grün": "Green", "gruen": "Green", "blau": "Blue", "rot": "Red", "rosa": "Pink", "braun": "Brown",
         "lila": "Purple", "violett": "Purple", "silber": "Silver", "kaltweiß": "Cold White", "kaltweiss": "Cold White"}
farbe = DE_EN.get(farbe.strip().lower(), farbe)
def hintergrund_laden():
    if os.fork() == 0:
        try:
            os.setsid()
            os.close(0); os.close(1); os.close(2)
            laden()
        finally:
            os._exit(0)

if not aktuell():
    vorhanden = all(os.path.exists(pfad(n)) for n in DATEIEN)
    hintergrund_laden()
    if not vorhanden:
        print(json.dumps({"fehler": "Datenbank wird geladen (einmalig), bitte in 1 Minute erneut"}))
        raise SystemExit

try:
    brands = {r["id"]: r.get("name", "") for r in lies("brands")}
    mats = {r["id"]: r.get("material", "") for r in lies("materials")}
    fil = {r["id"]: r for r in lies("filaments")}
    var = lies("variants")
    sizes = lies("sizes")
except Exception as e:
    print(json.dumps({"fehler": "Datenbank nicht lesbar: " + str(e)}))
    raise SystemExit

sz = {}
for s in sizes:
    sz.setdefault(s.get("variant_id"), []).append(s)

ean_n, herst_n, mat_n, farbe_n = ean_norm(ean), nm(herst), nm(mat), nm(farbe)
rgb = hexrgb(hexw)
try:
    gew_f = float(gew)
except Exception:
    gew_f = 0.0
if not (ean_n or farbe_n or rgb):
    print(json.dumps({"treffer": []}))
    raise SystemExit

treffer = []
for v in var:
    f = fil.get(v.get("filament_id"))
    if not f:
        continue
    m = mats.get(f.get("material_id"), "") or f.get("material", "")
    marke = brands.get(f.get("brand_id"), "")
    gr = sz.get(v.get("id"), [])
    ean_treffer = [s for s in gr if ean_n and ean_norm(s.get("gtin")) == ean_n]
    score = 0
    if ean_treffer:
        score += 100
    # Sorte muss passen (PLA+ != PLA+ 2.0), Klasse allein (PETG) passt schwaecher
    fn_ = nm(f.get("name"))
    if mat_n:
        if mat_n in (fn_, nm(m) + fn_) or (mat_n == nm(m) and fn_ == nm(m)):
            score += 25
        elif mat_n == nm(m):
            score += 5
        else:
            continue
    bn = nm(marke)
    if herst_n:
        if bn == herst_n:
            score += 30
        elif herst_n in bn or bn in herst_n:
            score += 15
        elif not ean_treffer:
            continue
    fn = nm(v.get("name"))
    c = v.get("color_hex") or ""
    farb_ok = False
    if farbe_n and (farbe_n in fn or (fn and fn in farbe_n)):
        score += 20
        if farbe_n == fn:
            score += 10
        farb_ok = True
    vr = hexrgb(c)
    if rgb and vr:
        d = sum((a - b) ** 2 for a, b in zip(rgb, vr)) ** 0.5
        if d < 25:
            score += 15
            farb_ok = True
    if not ean_treffer and (farbe_n or rgb) and not farb_ok:
        continue
    gs = ean_treffer[0] if ean_treffer else None
    if not gs:
        gleich = [s for s in gr if gew_f and abs(float(s.get("filament_weight") or 0) - gew_f) < 1]
        gs = gleich[0] if gleich else (gr[0] if gr else None)
        if gleich:
            score += 5
    if score < 40:
        continue
    g = None
    try:
        g = float(gs.get("filament_weight")) if gs else None
    except Exception:
        g = None
    sorte = f.get("name") or m
    label = (marke + " " + sorte + " " + (v.get("name") or "")).strip()
    if g:
        label += " " + (str(round(g / 1000, 2)).rstrip("0").rstrip(".")) + " kg"
    if ean_treffer:
        label += " (EAN)"
    treffer.append({"score": score, "label": label[:95], "hersteller": marke, "material": sorte, "klasse": m, "farbe": v.get("name") or "",
                    "hex": c.lstrip("#").upper(), "ean": (gs.get("gtin") or "") if gs else "", "gewicht": g or 0,
                    "dichte": f.get("density") or ""})
treffer.sort(key=lambda t: -t["score"])
seen, out = set(), []
for t in treffer:
    if t["label"] in seen:
        continue
    seen.add(t["label"])
    out.append(t)
    if len(out) == 3:
        break
os.makedirs(DIR, exist_ok=True)
json.dump(out, open(LAST, "w"), ensure_ascii=False)
print(json.dumps({"treffer": [t["label"] for t in out]}, ensure_ascii=False))
