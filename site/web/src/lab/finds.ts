// LAB ONLY (Job 1): "Past finds", public fungi records from iNaturalist and GBIF (data/finds.json,
// made by experiments/01-past-finds). A button on the map turns the layer on; a small panel filters
// by years, months and group, and can play through the years. Tapping a dot shows the record:
// photo (linked from its original address, never copied, only when its licence allows reuse),
// name, date, credit line and a link to the original record.
// Dots: solid = location known to within 500 m; faded = rough or unknown location;
// hollow ring = location blurred on purpose by the source (kept blurred here).
import * as maplibregl from "maplibre-gl";
import "../styles/finds.css";

type Group = "mushroom" | "lichen" | "other" | "unknown";
interface Rec {
  id: string; name: string | null; common: string | null; date: string | null; year: number | null; month: number | null;
  lat: number; lon: number; acc_m: number | null; loc: "good" | "rough" | "obscured"; group: Group; kind: string;
  source: string; link: string; observer: string | null; licence: string;
  photo: { url: string; licence: string; credit: string | null } | null; has_photo: boolean; district: string;
}

const COLOURS: Record<Group, string> = { mushroom: "#d6336c", lichen: "#1c7ed6", other: "#6741d9", unknown: "#868e96" };
const GROUPS: [Group, string][] = [["mushroom", "Mushrooms"], ["lichen", "Lichens"], ["other", "Other fungi"], ["unknown", "Not named"]];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const FIRST_YEAR = 1980;                       // older records (about 30) are kept in the "before" step of the slider
const LAYER = "finds-dot";

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

export class PastFinds {
  private recs: Rec[] = [];
  private on = false;
  private from = FIRST_YEAR - 1;               // FIRST_YEAR - 1 means "all years before FIRST_YEAR too"
  private to = new Date().getFullYear();
  private months = new Set<number>();          // empty = all months
  private groups = new Set<Group>(["mushroom", "lichen", "other", "unknown"]);
  private timer = 0;
  private panel: HTMLElement;
  private btn!: HTMLButtonElement;
  private card: HTMLElement;                   // the tapped record (docked card, not a map popup: it fits phones)
  private ring: maplibregl.Marker;

  constructor(private map: maplibregl.Map, private dataUrl: string, stage: HTMLElement) {
    this.panel = document.createElement("section");
    this.panel.className = "finds-panel";
    this.panel.hidden = true;
    this.panel.setAttribute("aria-label", "Past finds filters");
    this.card = document.createElement("section");
    this.card.className = "find-card";
    this.card.hidden = true;
    this.card.setAttribute("aria-label", "Past find record");
    stage.append(this.panel, this.card);
    const ringEl = document.createElement("div");
    ringEl.className = "find-ring";
    ringEl.setAttribute("aria-hidden", "true");
    this.ring = new maplibregl.Marker({ element: ringEl });
  }

  private closeCard() { this.card.hidden = true; this.ring.remove(); }

  /** The map button (a MapLibre control). */
  control(): maplibregl.IControl {
    return {
      onAdd: () => {
        const div = document.createElement("div");
        div.className = "maplibregl-ctrl maplibregl-ctrl-group";
        this.btn = document.createElement("button");
        this.btn.type = "button";
        this.btn.className = "ctrl-finds";
        this.btn.innerHTML = `<span class="finds-dot-icon" aria-hidden="true"></span><span>Past finds</span>`;
        this.btn.setAttribute("aria-pressed", "false");
        this.btn.dataset.tip = "Lab: public fungi records from iNaturalist and GBIF.";
        this.btn.addEventListener("click", () => this.toggle());
        div.append(this.btn);
        return div;
      },
      onRemove: () => this.btn.parentElement?.remove(),
    };
  }

  private async toggle() {
    this.on = !this.on;
    this.btn.setAttribute("aria-pressed", String(this.on));
    this.btn.classList.toggle("on", this.on);
    if (this.on && !this.recs.length) {
      this.btn.classList.add("busy");
      try {
        const d = await fetch(this.dataUrl, { cache: "no-cache" }).then((r) => r.json());
        this.recs = d.records as Rec[];
      } catch {
        this.panel.hidden = false;
        this.panel.innerHTML = `<p class="fp-note">Could not load the finds file.</p>`;
        return;
      } finally { this.btn.classList.remove("busy"); }
      this.addLayer();
      this.renderPanel();
    }
    this.panel.hidden = !this.on;
    if (this.map.getLayer(LAYER)) this.map.setLayoutProperty(LAYER, "visibility", this.on ? "visible" : "none");
    if (!this.on) { this.stop(); this.closeCard(); }
    document.documentElement.classList.toggle("finds-on", this.on);
  }

  private addLayer() {
    const fc: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features: this.recs.map((r, i) => ({
        type: "Feature", id: i, geometry: { type: "Point", coordinates: [r.lon, r.lat] },
        properties: { i, g: r.group, loc: r.loc, y: r.year ?? 0, m: r.month ?? 0 },
      })),
    };
    this.map.addSource("finds", { type: "geojson", data: fc });
    const colour: maplibregl.ExpressionSpecification = ["match", ["get", "g"],
      "mushroom", COLOURS.mushroom, "lichen", COLOURS.lichen, "other", COLOURS.other, COLOURS.unknown];
    this.map.addLayer({
      id: LAYER, type: "circle", source: "finds",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 4, 12, 6, 15, 8],
        "circle-color": colour,
        "circle-opacity": ["match", ["get", "loc"], "good", 0.95, "rough", 0.4, 0.08],
        "circle-stroke-color": ["match", ["get", "loc"], "obscured", colour, "#ffffff"],
        "circle-stroke-width": ["match", ["get", "loc"], "obscured", 2, "good", 1.5, 0.8],
        "circle-stroke-opacity": ["match", ["get", "loc"], "rough", 0.6, 1],
      },
    });
    this.applyFilter();
  }

  private filterExpr(): maplibregl.FilterSpecification {
    const all: unknown[] = ["all", ["in", ["get", "g"], ["literal", [...this.groups]]]];
    if (this.from >= FIRST_YEAR) all.push([">=", ["get", "y"], this.from]);
    if (this.to < new Date().getFullYear()) all.push(["<=", ["get", "y"], this.to], [">", ["get", "y"], 0]);
    if (this.months.size) all.push(["in", ["get", "m"], ["literal", [...this.months]]]);
    return all as maplibregl.FilterSpecification;
  }

  private shown(r: Rec) {
    if (!this.groups.has(r.group)) return false;
    if (this.from >= FIRST_YEAR && (r.year ?? 0) < this.from) return false;
    if (this.to < new Date().getFullYear() && (!r.year || r.year > this.to)) return false;
    if (this.months.size && !this.months.has(r.month ?? 0)) return false;
    return true;
  }

  private applyFilter() {
    if (this.map.getLayer(LAYER)) this.map.setFilter(LAYER, this.filterExpr());
    const n = this.recs.filter((r) => this.shown(r)).length;
    const c = this.panel.querySelector(".fp-count");
    if (c) c.textContent = `${n.toLocaleString("en")} of ${this.recs.length.toLocaleString("en")} records`;
    const yl = this.panel.querySelector(".fp-years");
    if (yl) yl.textContent = this.from === this.to ? String(this.from)
      : `${this.from < FIRST_YEAR ? `before ${FIRST_YEAR}` : this.from} – ${this.to}`;
  }

  private renderPanel() {
    const nowY = new Date().getFullYear();
    this.panel.innerHTML = `
      <div class="fp-head">
        <strong>Past finds</strong> <span class="fp-count" aria-live="polite"></span>
        <button type="button" class="fp-play" aria-label="Play through the years">▶ Play</button>
      </div>
      <div class="fp-row"><span class="fp-label">Years</span> <span class="fp-years"></span></div>
      <div class="fp-range">
        <input type="range" class="fp-from" min="${FIRST_YEAR - 1}" max="${nowY}" value="${this.from}" aria-label="From year">
        <input type="range" class="fp-to" min="${FIRST_YEAR - 1}" max="${nowY}" value="${this.to}" aria-label="To year">
      </div>
      <div class="fp-chips fp-months" role="group" aria-label="Months">
        <button type="button" data-m="0" aria-pressed="true">All</button>
        ${MONTHS.map((m, i) => `<button type="button" data-m="${i + 1}" aria-pressed="false">${m}</button>`).join("")}
      </div>
      <div class="fp-chips fp-groups" role="group" aria-label="Groups">
        ${GROUPS.map(([g, label]) => `<button type="button" data-g="${g}" aria-pressed="true"><span class="sw" style="background:${COLOURS[g]}"></span>${label}</button>`).join("")}
      </div>
      <div class="fp-key">
        <span><i class="k good"></i>Exact spot</span><span><i class="k rough"></i>Rough spot</span><span><i class="k obscured"></i>Blurred on purpose</span>
      </div>
      <p class="fp-note">Public records of what people saw. A record says nothing about eating.</p>`;
    const from = this.panel.querySelector<HTMLInputElement>(".fp-from")!;
    const to = this.panel.querySelector<HTMLInputElement>(".fp-to")!;
    const onRange = (e: Event) => {
      this.stop();
      let a = Number(from.value), b = Number(to.value);
      if (a > b) { if (e.target === from) b = a; else a = b; from.value = String(a); to.value = String(b); }
      this.from = a; this.to = b; this.applyFilter();
    };
    from.addEventListener("input", onRange);
    to.addEventListener("input", onRange);
    this.panel.querySelector(".fp-months")!.addEventListener("click", (e) => {
      const b = (e.target as HTMLElement).closest<HTMLButtonElement>("button");
      if (!b) return;
      const m = Number(b.dataset.m);
      if (m === 0) this.months.clear(); else if (this.months.has(m)) this.months.delete(m); else this.months.add(m);
      this.panel.querySelectorAll<HTMLButtonElement>(".fp-months button").forEach((x) =>
        x.setAttribute("aria-pressed", String(Number(x.dataset.m) === 0 ? this.months.size === 0 : this.months.has(Number(x.dataset.m)))));
      this.applyFilter();
    });
    this.panel.querySelector(".fp-groups")!.addEventListener("click", (e) => {
      const b = (e.target as HTMLElement).closest<HTMLButtonElement>("button");
      if (!b) return;
      const g = b.dataset.g as Group;
      if (this.groups.has(g)) { if (this.groups.size > 1) this.groups.delete(g); } else this.groups.add(g);
      b.setAttribute("aria-pressed", String(this.groups.has(g)));
      this.applyFilter();
    });
    this.panel.querySelector(".fp-play")!.addEventListener("click", () => (this.timer ? this.stop() : this.play()));
    this.applyFilter();
  }

  /** Play: one year at a time, only years that have records for the chosen groups and months. */
  private play() {
    const btn = this.panel.querySelector<HTMLButtonElement>(".fp-play")!;
    const years = [...new Set(this.recs.filter((r) => r.year && r.year >= FIRST_YEAR && this.groups.has(r.group)
      && (!this.months.size || this.months.has(r.month ?? 0))).map((r) => r.year!))].sort((x, y) => x - y);
    if (!years.length) return;
    // Start where the slider starts; if one year is showing, carry on after it.
    const start = this.from === this.to ? this.to + 1 : this.from;
    let k = Math.max(0, years.findIndex((y) => y >= start));
    if (years[k] < start) k = 0;
    const step = () => {
      const y = years[k];
      this.from = this.to = y;
      this.panel.querySelector<HTMLInputElement>(".fp-from")!.value = String(y);
      this.panel.querySelector<HTMLInputElement>(".fp-to")!.value = String(y);
      this.applyFilter();
      if (++k >= years.length) this.stop();
    };
    btn.textContent = "❚❚ Stop"; btn.setAttribute("aria-label", "Stop playing");
    step();
    if (k < years.length) this.timer = window.setInterval(step, 1000);
  }

  private stop() {
    if (!this.timer) return;
    window.clearInterval(this.timer); this.timer = 0;
    const btn = this.panel.querySelector<HTMLButtonElement>(".fp-play");
    if (btn) { btn.textContent = "▶ Play"; btn.setAttribute("aria-label", "Play through the years"); }
  }

  /** Called by the map's tap handler first: true when a dot was tapped (then no square card opens). */
  tap(point: maplibregl.Point): boolean {
    if (!this.on || !this.map.getLayer(LAYER)) return false;
    const pad = 10;
    const hits = this.map.queryRenderedFeatures([[point.x - pad, point.y - pad], [point.x + pad, point.y + pad]], { layers: [LAYER] });
    if (!hits.length) { this.closeCard(); return false; }
    const list = [...new Set(hits.map((h) => Number(h.properties!.i)))].map((i) => this.recs[i])
      .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
    this.show(list, 0);
    return true;
  }

  private show(list: Rec[], k: number) {
    const r = list[k];
    const httpsPhoto = r.photo && r.photo.url.startsWith("https://") ? r.photo : null;
    const where = r.loc === "good" ? `Location within ${r.acc_m} m`
      : r.loc === "obscured" ? "Location blurred on purpose by the source"
      : r.acc_m ? `Rough location (± ${r.acc_m >= 1000 ? `${Math.round(r.acc_m / 1000)} km` : `${r.acc_m} m`})` : "Location accuracy not given";
    const date = r.date ? new Date(r.date + (r.date.length === 7 ? "-01" : "")).toLocaleDateString("en-GB",
      r.date.length === 7 ? { month: "long", year: "numeric" } : { day: "numeric", month: "short", year: "numeric" }) : "Date not given";
    const credit = httpsPhoto ? esc(httpsPhoto.credit ?? `© ${r.observer ?? "unknown"} (${httpsPhoto.licence})`)
      : `Record by ${esc(r.observer ?? "unknown")} · ${esc(r.licence)}`;
    const html = `
      ${httpsPhoto ? `<a href="${esc(r.link)}" target="_blank" rel="noopener"><img class="fp-photo" src="${esc(httpsPhoto.url)}" alt="Photo of ${esc(r.name)}" loading="lazy" referrerpolicy="no-referrer"></a>`
        : `<div class="fp-nophoto">${r.has_photo ? "Photo only at the source (its licence does not allow showing it here)" : "No photo"}</div>`}
      <div class="fp-name"><em>${esc(r.name ?? "Not named")}</em>${r.common ? ` <span>(${esc(r.common)})</span>` : ""}</div>
      <div class="fp-meta">${esc(date)} · ${esc(r.kind)}</div>
      <div class="fp-meta">${esc(where)} · ${esc(r.district)}</div>
      <div class="fp-credit">${credit}</div>
      <div class="fp-links"><a href="${esc(r.link)}" target="_blank" rel="noopener">Open the original record (${esc(r.source)}) ↗</a></div>
      ${list.length > 1 ? `<div class="fp-pager"><button type="button" data-k="${k - 1}" ${k === 0 ? "disabled" : ""} aria-label="Previous record">‹</button>
        <span>${k + 1} of ${list.length} here</span>
        <button type="button" data-k="${k + 1}" ${k === list.length - 1 ? "disabled" : ""} aria-label="Next record">›</button></div>` : ""}`;
    this.card.innerHTML = `<button type="button" class="fc-close" aria-label="Close the record">×</button>${html}`;
    this.card.hidden = false;
    this.card.querySelector(".fc-close")!.addEventListener("click", () => this.closeCard());
    this.card.querySelectorAll<HTMLButtonElement>(".fp-pager button").forEach((b) =>
      b.addEventListener("click", () => this.show(list, Number(b.dataset.k))));
    this.ring.setLngLat([r.lon, r.lat]).addTo(this.map);
  }
}
