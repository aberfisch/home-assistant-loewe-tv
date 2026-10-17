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
    if (state?.attributes?.source === this._pendingMode) this._pendingMode = null;
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
    const mode = ["TV", "Radio", "HDMI1", "HDMI2", "HDMI3", "HDMI4"].includes(attrs.source) ? attrs.source : null;
    const rawTitle = attrs.media_title || "";
    const technicalTitle = /^(channel:\/\/|dvb:\/\/|extav:\/\/|scart:\/\/|live:\/\/|[0-9a-f]{8}-[0-9a-f-]{20,})/i.test(rawTitle);
    const current = mode?.startsWith("HDMI") ? mode : (!technicalTitle && rawTitle ? rawTitle : mode || "Quelle nicht erkannt");
    const isHdmi = mode?.startsWith("HDMI") || false;
    const typed = attrs.loewe_channels_by_type;
    const classified = mode === "Radio" ? typed?.Radio : mode === "TV" ? typed?.TV : null;
    const visibleChannels = Array.isArray(classified) && classified.length ? classified : channels;
    const epgTitle = attrs.loewe_epg_title || "";
    const epgTime = attrs.loewe_epg_time || "";
    const online = state && !["unavailable", "unknown"].includes(state.state);
    const on = online && state.state !== "off";
    const statusText = !online ? "Nicht verfügbar" : on ? "Eingeschaltet" : "Ausgeschaltet";
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
        .display {cursor:pointer}
        .picker {padding:12px;border-radius:12px;background:var(--secondary-background-color,#303239);margin:10px 0}
        .picker[hidden] {display:none}
        .picker input {width:100%;box-sizing:border-box;padding:10px;background:transparent;color:inherit;border:1px solid #777;border-radius:8px}
        .choices {max-height:240px;overflow:auto}
        .choices button {display:block;width:100%;text-align:left;margin:3px 0}
        .display .label {font-size:11px;letter-spacing:1.4px;text-transform:uppercase;opacity:.6}
        .channel {font-size:24px;font-weight:650;line-height:1.3;margin-top:10px;overflow-wrap:anywhere}
        .subtitle {font-size:12px;opacity:.65;margin-top:8px}
        button {font:inherit;cursor:pointer;border:0;border-radius:12px;min-height:43px;padding:10px 14px;background:var(--secondary-background-color,#35373c);color:inherit}
        button:focus-visible,select:focus-visible,input:focus-visible {outline:2px solid var(--loewe-accent);outline-offset:2px}
        button:disabled {opacity:.35;cursor:not-allowed}
        button.primary {background:var(--loewe-accent);color:#141414;font-weight:700}
        button.power {font-size:22px;min-width:50px;border:2px solid transparent}
        button.power.on {background:#1c7144;color:#fff;border-color:#40b879}
        button.power.off {background:var(--secondary-background-color,#35373c);color:var(--secondary-text-color,#bbb);border-color:var(--divider-color,#777)}
        .power-group {display:flex;align-items:center;gap:10px}
        .power-status {display:flex;align-items:center;gap:7px;font-size:13px;font-weight:700;white-space:nowrap}
        .power-dot {width:11px;height:11px;border-radius:50%;background:#929292}
        .power-status.on .power-dot {background:#35bb75;box-shadow:0 0 0 3px rgba(53,187,117,.18)}
        .power-status.off .power-dot {background:#999}
        .power-status.unknown .power-dot {background:#d9a441}
        .transport {margin:16px 0}
        .transport button {flex:1;font-size:17px}
        .transport button.primary {flex:0 1 auto;font-size:14px;min-width:88px;max-width:150px;padding:9px 12px}
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
          <div class="power-group"><div class="power-status ${!online ? "unknown" : on ? "on" : "off"}" role="status"><span class="power-dot"></span>${esc(statusText)}</div><button class="power ${on ? "on" : "off"}" data-action="power" aria-label="${on ? "Fernseher ausschalten" : "Fernseher einschalten"}" title="${on ? "Ausschalten" : "Einschalten"}">⏻</button></div></div>
        <div class="display" id="channel-display" role="button" tabindex="0">
          <div class="label">${isHdmi ? "Aktueller Eingang" : mode ? "Aktueller Sender · Zum Auswählen klicken ⌄" : "Aktuelle Quelle unbekannt"}</div>
          <div class="channel">${esc(current)}</div>
          <div class="subtitle">${esc(!online ? "Nicht verfügbar" : on ? (mode || "Quelle nicht erkannt") : "Ausgeschaltet")}</div>
          ${epgTitle ? `<div class="subtitle">${esc(epgTitle)} ${esc(epgTime)}</div>` : ""}
        </div>
        <div class="picker" id="channel-picker" hidden>
          <input id="channel-search" placeholder="Sender suchen …" aria-label="Sender suchen">
          <div class="choices" id="channel-choices"></div>
          ${mode === "Radio" && !visibleChannels.length ? `<div class="subtitle">Die TV-/Radio-Zuordnung ist noch nicht verfügbar. Es werden alle Sender angezeigt.</div>` : ""}
        </div>
        <div class="transport">
          <button data-action="previous" ${isHdmi ? "disabled" : ""}>◀ P−</button>
          <button class="primary" data-action="sources">${esc(mode || "Quelle wählen")} ⌄</button>
          <button data-action="next" ${isHdmi ? "disabled" : ""}>P+ ▶</button>
        </div>
        <div class="picker" id="source-picker" hidden>
          ${inputs.map(src => `<button data-source="${esc(src)}">${esc(src)}</button>`).join("")}
        </div>
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

          mute: ["volume_mute", {is_volume_muted: !attrs.is_volume_muted}],
          "vol-down": ["volume_down", {}], "vol-up": ["volume_up", {}]
        };
        if (action === "sources") {
          const p = this.shadowRoot.getElementById("source-picker");
          p.hidden = !p.hidden;
          this.shadowRoot.getElementById("channel-picker").hidden = true;
        } else if (actions[action]) this.call(...actions[action]);
      });
    });
    this.shadowRoot.querySelectorAll("[data-source]").forEach(button => button.addEventListener("click", () => {
      this.call("select_source", {source: button.dataset.source});
      this.shadowRoot.getElementById("source-picker").hidden = true;
    }));
    const display = this.shadowRoot.getElementById("channel-display");
    const picker = this.shadowRoot.getElementById("channel-picker");
    const search = this.shadowRoot.getElementById("channel-search");
    const choices = this.shadowRoot.getElementById("channel-choices");
    const populate = () => {
      choices.replaceChildren();
      const q = search.value.toLocaleLowerCase();
      visibleChannels.filter(s => s.toLocaleLowerCase().includes(q)).slice(0, 150).forEach(channel => {
        const button = document.createElement("button");
        button.textContent = channel.replace(/^Sender: /, "");
        button.addEventListener("click", () => {
          this.call("select_source", {source: channel});
          picker.hidden = true;
        });
        choices.append(button);
      });
      if (!choices.children.length) choices.textContent = "Keine passenden Sender";
    };
    const toggle = () => {
      if (isHdmi) return;
      picker.hidden = !picker.hidden;
      this.shadowRoot.getElementById("source-picker").hidden = true;
      if (!picker.hidden) { populate(); search.focus(); }
    };
    display.addEventListener("click", toggle);
    display.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
    });
    search.addEventListener("input", populate);
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
