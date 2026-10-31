/*
 * 3D Print Manager – Typenschild-Foto-Upload-Karte
 * Version 0.1.0-beta · Lizenz GPL-3.0
 *
 * Drag & Drop (PC) bzw. Kamera (Handy). Das Foto wird verkleinert, nach
 * Medien → filament_fotos hochgeladen und danach automatisch per KI ausgewertet.
 *
 * Verwendung im Dashboard:
 *   type: custom:pm-foto-upload-card
 * Optionen (alle optional):
 *   ordner:        filament_fotos                  (Unterordner in "Mein Medium")
 *   skript:        script.pm_foto_auswerten        (wird nach dem Upload ausgeführt)
 *   vorbereitung:  shell_command.pm_neuestes_foto  (legt den Ordner an)
 *   max_pixel:     1600                            (längste Bildkante)
 */
const PM_VERSION = "0.1.0-beta";

class PmFotoUploadCard extends HTMLElement {
  setConfig(config) {
    this._c = Object.assign({
      ordner: "filament_fotos",
      skript: "script.pm_foto_auswerten",
      vorbereitung: "shell_command.pm_neuestes_foto",
      max_pixel: 1600,
    }, config || {});
    this._render();
  }

  set hass(hass) { this._hass = hass; }
  getCardSize() { return 3; }
  getGridOptions() { return { columns: 12, rows: 3, min_rows: 3 }; }

  _render() {
    if (this.shadowRoot) return;
    const r = this.attachShadow({ mode: "open" });
    r.innerHTML = `
      <style>
        ha-card { padding: 12px; height: 100%; box-sizing: border-box; }
        .zone { border: 2px dashed var(--divider-color); border-radius: var(--ha-card-border-radius, 12px);
                padding: 14px; text-align: center; cursor: pointer; transition: all .15s ease;
                display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%;
                box-sizing: border-box; justify-content: center; }
        .zone.over { border-color: var(--primary-color); background: rgba(var(--rgb-primary-color, 3,169,244), .08); }
        .zone.busy { opacity: .7; cursor: progress; }
        ha-icon { --mdc-icon-size: 36px; color: var(--primary-color); }
        .t { font-weight: 500; color: var(--primary-text-color); }
        .s { font-size: .85em; color: var(--secondary-text-color); }
        .btns { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
        button { font: inherit; border: none; border-radius: 18px; padding: 7px 14px; cursor: pointer;
                 background: var(--primary-color); color: var(--text-primary-color, #fff); }
        button.sek { background: var(--secondary-background-color); color: var(--primary-text-color); }
        img { max-height: 90px; max-width: 100%; border-radius: 8px; }
        .st { font-size: .9em; min-height: 1.2em; }
        .st.ok { color: var(--success-color, #43a047); }
        .st.err { color: var(--error-color, #db4437); }
      </style>
      <ha-card>
        <div class="zone" id="zone">
          <ha-icon icon="mdi:camera-plus-outline"></ha-icon>
          <div class="t">Typenschild-Foto hierher ziehen</div>
          <div class="btns">
            <button id="cam">📷 Kamera</button>
            <button id="file" class="sek">🖼️ Datei wählen</button>
          </div>
          <img id="pv" hidden>
          <div id="st" class="st s">Nach dem Hochladen liest die KI Hersteller, Material, Farbe und Barcode aus.</div>
        </div>
        <input type="file" id="inCam" accept="image/*" capture="environment" hidden>
        <input type="file" id="inFile" accept="image/*" hidden>
      </ha-card>`;
    const $ = (id) => r.getElementById(id);
    const zone = $("zone");
    $("cam").addEventListener("click", (e) => { e.stopPropagation(); if (!this._busy) $("inCam").click(); });
    $("file").addEventListener("click", (e) => { e.stopPropagation(); if (!this._busy) $("inFile").click(); });
    zone.addEventListener("click", () => { if (!this._busy) $("inFile").click(); });
    for (const id of ["inCam", "inFile"]) {
      $(id).addEventListener("change", (e) => {
        const f = e.target.files && e.target.files[0];
        e.target.value = "";
        if (f) this._verarbeite(f);
      });
    }
    zone.addEventListener("dragover", (e) => { e.preventDefault(); zone.classList.add("over"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("over"));
    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      zone.classList.remove("over");
      const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (f && !this._busy) this._verarbeite(f);
    });
  }

  _status(text, art) {
    const st = this.shadowRoot.getElementById("st");
    st.textContent = text;
    st.className = "st " + (art || "s");
  }

  async _verkleinern(file) {
    try {
      const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
      const f = Math.min(1, this._c.max_pixel / Math.max(bmp.width, bmp.height));
      const c = document.createElement("canvas");
      c.width = Math.round(bmp.width * f);
      c.height = Math.round(bmp.height * f);
      c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
      return await new Promise((res) => c.toBlob((b) => res(b || file), "image/jpeg", 0.85));
    } catch (e) {
      return file; // z. B. HEIC in Browsern ohne Unterstützung: Original hochladen
    }
  }

  async _verarbeite(file) {
    if (!this._hass) return;
    if (!file.type.startsWith("image/")) { this._status("Bitte ein Bild auswählen.", "err"); return; }
    this._busy = true;
    const zone = this.shadowRoot.getElementById("zone");
    zone.classList.add("busy");
    try {
      this._status("Bild wird vorbereitet …");
      const blob = await this._verkleinern(file);
      const pv = this.shadowRoot.getElementById("pv");
      pv.src = URL.createObjectURL(blob);
      pv.hidden = false;

      // Ordner sicherstellen (legt filament_fotos an, falls noch nicht vorhanden)
      try {
        const [d, s] = this._c.vorbereitung.split(".");
        await this._hass.callService(d, s, {});
      } catch (e) { /* optional */ }

      this._status("Lade hoch …");
      const z = new Date(), p = (n) => String(n).padStart(2, "0");
      const name = `typenschild_${z.getFullYear()}${p(z.getMonth() + 1)}${p(z.getDate())}_${p(z.getHours())}${p(z.getMinutes())}${p(z.getSeconds())}.jpg`;
      const fd = new FormData();
      fd.append("media_content_id", `media-source://media_source/local/${this._c.ordner}`);
      fd.append("file", blob, name);
      const resp = await this._hass.fetchWithAuth("/api/media_source/local_source/upload", { method: "POST", body: fd });
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) throw new Error("Hochladen ist nur für Administratoren erlaubt.");
        throw new Error("Upload fehlgeschlagen (" + resp.status + "): " + (await resp.text()).slice(0, 120));
      }

      this._status("🤖 KI liest das Typenschild …");
      const [sd, ss] = this._c.skript.split(".");
      await this._hass.callService(sd, ss, {});
      this._status("✅ Erkannt – bitte die Felder unten prüfen und ergänzen.", "ok");
    } catch (e) {
      this._status("❌ " + (e && e.message ? e.message : e), "err");
    } finally {
      this._busy = false;
      zone.classList.remove("busy");
    }
  }
}

customElements.define("pm-foto-upload-card", PmFotoUploadCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "pm-foto-upload-card",
  name: "3D Print Manager – Typenschild-Foto",
  description: "Drag & Drop / Kamera-Upload mit automatischer KI-Auswertung (v" + PM_VERSION + ")",
});
console.info("%c 3D-PRINT-MANAGER %c Foto-Upload-Karte v" + PM_VERSION, "background:#03a9f4;color:#fff;padding:2px 4px;border-radius:3px", "");
