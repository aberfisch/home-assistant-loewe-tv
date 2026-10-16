/* Loewe TV card — standalone Lovelace custom element, no dependencies. */
class LoeweTVCard extends HTMLElement {
  static getConfigElement() { return document.createElement("loewe-tv-card-editor"); }
  static getStubConfig() { return { type: "custom:loewe-tv-card" }; }
  setConfig(config) {
    if (!config || typeof config !== "object") throw new Error("Invalid Loewe TV card configuration");
    this.config = config;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this.render();
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.config) return;
    const entity = this.entityId();
    const state = hass.states[entity];
    const key = JSON.stringify([entity, state?.state, state?.attributes, hass.language]);
    if (key !== this._lastKey) { this._lastKey = key; this.render(); }
  }
  entityId() {
    if (this.config.entity) return this.config.entity;
    return Object.keys(this._hass?.states || {}).find(id => id.startsWith("media_player.") &&
      (id.includes("loewe") || this._hass.states[id].attributes?.friendly_name?.toLowerCase().includes("loewe"))) || "";
  }
  call(service, data = {}) {
    const entity_id = this.entityId();
    if (!entity_id || !this._hass?.states[entity_id]) return;
    this._hass.callService("media_player", service, { entity_id, ...data }).catch(err => {
      const notice = this.shadowRoot?.querySelector("#notice");
      if (notice) notice.textContent = err?.message || "Aktion fehlgeschlagen";
    });
  }
  render() {
    if (!this.shadowRoot || !this.config) return;
    const entity = this.entityId();
    const state = this._hass?.states[entity];
    const attrs = state?.attributes || {};
    const sources = Array.isArray(attrs.source_list) ? attrs.source_list : [];
    const channels = sources.filter(s => s.startsWith("Sender: "));
    const inputs = sources.filter(s => !s.startsWith("Sender: "));
    const current = attrs.media_title || attrs.source || "Keine Wiedergabeinformationen";
    const online = state && !["unavailable", "unknown"].includes(state.state);
    const on = online && state.state !== "off";
    const volume = Math.round((Number(attrs.volume_level) || 0) * 100);
    const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
    this.shadowRoot.innerHTML = `
      <style>
        :host {display:block;--loewe-accent:var(--primary-color,#b69a6c)}
        ha-card {overflow:hidden;background:var(--ha-card-background,var(--card-background-color,#202127));color:var(--primary-text-color,#fff);border-radius:22px;padding:22px;box-sizing:border-box}
        .top,.section,.transport,.vol,.actions {display:flex;align-items:center;justify-content:space-between;gap:12px}
        .eyebrow {font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:.65}
        h2 {font-size:23px;font-weight:600;margin:5px 0 0}
        .display {margin:22px 0 18px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#222c39,#10151d);color:#fff;min-height:95px;box-sizing:border-box}
        .display .label {font-size:11px;letter-spacing:1.4px;text-transform:uppercase;opacity:.6}
        .channel {font-size:24px;font-weight:650;line-height:1.3;margin-top:10px;overflow-wrap:anywhere}
        .subtitle {font-size:12px;opacity:.65;margin-top:8px}
        button {font:inherit;cursor:pointer;border:0;border-radius:12px;min-height:43px;padding:10px 14px;background:var(--secondary-background-color,#35373c);color:inherit}
        button:focus-visible,select:focus-visible,input:focus-visible {outline:2px solid var(--loewe-accent);outline-offset:2px}
        button:disabled {opacity:.35;cursor:not-allowed}
        button.primary {background:var(--loewe-accent);color:#141414;font-weight:700}
        button.power {font-size:22px;min-width:50px}
        .transport {margin:16px 0}
        .transport button {flex:1;font-size:17px}
        .transport button.primary {flex:1.3;font-size:20px}
        .section {margin:20px 0 8px}
        .section label {font-size:12px;opacity:.7}
        .vol {margin-top:12px}
        .vol input {flex:1;min-width:0;accent-color:var(--loewe-accent)}
        .vol span {font-size:12px;min-width:35px;text-align:right}
        select {width:100%;padding:13px 12px;border:1px solid var(--divider-color,#444);border-radius:12px;background:var(--secondary-background-color,#303239);color:inherit;font:inherit;margin-top:9px}
        .footer {display:flex;justify-content:space-between;align-items:center;margin-top:20px;font-size:12px;opacity:.65}
        #notice {font-size:12px;color:var(--error-color,#e88);margin-top:8px;min-height:1em}
        @media(max-width:350px){ha-card{padding:14px}.channel{font-size:20px}}
      </style>
      <ha-card>
        <div class="top"><div><div class="eyebrow">Loewe · Home Assistant</div><h2>${esc(this.config.title || attrs.friendly_name || "Loewe TV")}</h2></div>
          <button class="power" data-action="power" aria-label="Ein/Aus">${on ? "⏻" : "⏻"}</button></div>
        <div class="display"><div class="label">Aktueller Sender / Eingang</div>
          <div class="channel">${esc(current)}</div><div class="subtitle">${esc(!online ? "Nicht verfügbar" : on ? (attrs.source || "TV eingeschaltet") : "Standby")}</div></div>
        <div class="section"><strong>Sender</strong><span class="eyebrow">DVB-C</span></div>
        <div class="transport">
          <button data-action="previous" aria-label="Vorheriger Sender">◀ P−</button>
          <button class="primary" data-action="tv" aria-label="Fernsehen">TV</button>
          <button data-action="next" aria-label="Nächster Sender">P+ ▶</button>
        </div>
        <label class="eyebrow" for="channels">Sender direkt auswählen</label>
        <select id="channels"><option value="">${channels.length ? "Sender auswählen …" : "Keine Senderliste verfügbar"}</option>
          ${channels.map(s => `<option value="${esc(s)}">${esc(s.slice(8))}</option>`).join("")}</select>
        <div class="section"><strong>Quellen</strong></div>
        <select id="sources"><option value="">Quelle auswählen …</option>
          ${inputs.map(s => `<option value="${esc(s)}" ${attrs.source === s ? "selected" : ""}>${esc(s)}</option>`).join("")}</select>
        <div class="section"><strong>Lautstärke</strong><button data-action="mute">${attrs.is_volume_muted ? "Ton an" : "Stumm"}</button></div>
        <div class="vol"><button data-action="vol-down" aria-label="Leiser">−</button>
          <input id="volume" type="range" min="0" max="100" step="1" value="${volume}" aria-label="Lautstärke">
          <button data-action="vol-up" aria-label="Lauter">+</button><span>${volume}%</span></div>
        <div id="notice"></div><div class="footer"><span>${esc(entity || "Keine Loewe-Mediaplayer-Entität gefunden")}</span><span>${on ? "● Aktiv" : "○ Standby"}</span></div>
      </ha-card>`;
    this.shadowRoot.querySelectorAll("button[data-action]").forEach(button => {
      button.addEventListener("click", () => {
        const action = button.dataset.action;
        const actions = {
          power: [on ? "turn_off" : "turn_on", {}],
          previous: ["media_previous_track", {}], next: ["media_next_track", {}],
          tv: ["select_source", {source: "TV"}],
          mute: ["volume_mute", {is_volume_muted: !attrs.is_volume_muted}],
          "vol-down": ["volume_down", {}], "vol-up": ["volume_up", {}]
        };
        if (actions[action]) this.call(...actions[action]);
      });
    });
    for (const id of ["channels", "sources"]) this.shadowRoot.getElementById(id).addEventListener("change", e => {
      if (e.target.value) this.call("select_source", {source: e.target.value});
    });
    this.shadowRoot.getElementById("volume").addEventListener("change", e => this.call("volume_set", {volume_level: Number(e.target.value)/100}));
  }
  getCardSize() { return 7; }
}
if (!customElements.get("loewe-tv-card")) customElements.define("loewe-tv-card", LoeweTVCard);
class LoeweTVCardEditor extends HTMLElement {
  setConfig(config) { this.config = config; this.render(); }
  set hass(hass) { this._hass = hass; this.render(); }
  render() {
    if (!this.config || !this._hass) return;
    const entities = Object.keys(this._hass.states).filter(id => id.startsWith("media_player."));
    this.innerHTML = '<div style="padding:12px"><label>Mediaplayer <select style="width:100%" id="entity"></select></label></div>';
    const select = this.querySelector("select");
    select.innerHTML = '<option value="">Automatisch erkennen</option>' + entities.map(id => '<option value="' + id + '">' + id + '</option>').join("");
    select.value = this.config.entity || "";
    select.addEventListener("change", e => {
      this.dispatchEvent(new CustomEvent("config-changed", {detail:{config:{...this.config,entity:e.target.value}},bubbles:true,composed:true}));
    });
  }
}
if (!customElements.get("loewe-tv-card-editor")) customElements.define("loewe-tv-card-editor", LoeweTVCardEditor);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === "loewe-tv-card")) window.customCards.push({
  type:"loewe-tv-card",name:"Loewe TV",description:"Loewe TV mit Sendersteuerung, Quellen und Lautstärke"
});
