// LAB ONLY (experiment 07): "Best areas this season". Each forest square ranked against all other
// forest squares for a month, from season x altitude and shade only (no daily weather). Made by
// experiments/07-rethink/export_areas.py -> data/lab_areas.pmtiles (properties r10 ... r4, 0-100).
// The colours compare forest squares with each other; they are not today's conditions.
import * as maplibregl from "maplibre-gl";
import { SCORE_STOPS } from "../map/layers";
import { labNotes } from "./notes";

const SRC = "lab-areas", FILL = "lab-areas-fill";
const MONTHS: [number, string][] = [[10, "Oct"], [11, "Nov"], [12, "Dec"], [1, "Jan"], [2, "Feb"], [3, "Mar"], [4, "Apr"]];

export class BestAreas {
  private on = false;
  private loaded = false;
  private btn!: HTMLButtonElement;
  private note: HTMLElement;
  private month: number;

  constructor(private map: maplibregl.Map, private url: string, stage: HTMLElement) {
    const now = new Date().getMonth() + 1;
    this.month = MONTHS.some(([m]) => m === now) ? now : 11;
    const grad = `linear-gradient(90deg, ${SCORE_STOPS.map(([v, c]) => `${c} ${v}%`).join(", ")})`;
    this.note = document.createElement("div");
    this.note.className = "lab-note areas-note";
    this.note.hidden = true;
    this.note.innerHTML = `<strong>Lab test: best areas this season</strong>
      <span>Season, altitude and shade only. No daily weather. Compares forest squares with each other, not today's conditions.</span>
      <div class="areas-bar" style="background:${grad}" aria-hidden="true"></div>
      <div class="areas-scale"><span>Lower</span><span aria-hidden="true">→</span><span>Top areas</span></div>
      <div class="areas-months" role="group" aria-label="Month">${MONTHS.map(([m, l]) =>
        `<button type="button" data-m="${m}" aria-pressed="${m === this.month}">${l}</button>`).join("")}</div>`;
    labNotes(stage).append(this.note);
    this.note.querySelector(".areas-months")!.addEventListener("click", (e) => {
      const b = (e.target as HTMLElement).closest<HTMLButtonElement>("button");
      if (!b) return;
      this.month = Number(b.dataset.m);
      this.note.querySelectorAll<HTMLButtonElement>(".areas-months button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      this.paint();
    });
  }

  control(): maplibregl.IControl {
    return {
      onAdd: () => {
        const div = document.createElement("div");
        div.className = "maplibregl-ctrl maplibregl-ctrl-group";
        this.btn = document.createElement("button");
        this.btn.type = "button";
        this.btn.className = "ctrl-finds ctrl-areas";
        this.btn.innerHTML = `<span class="areas-sw" aria-hidden="true"></span><span>Best areas</span>`;
        this.btn.setAttribute("aria-pressed", "false");
        this.btn.dataset.tip = "Lab test: forest ranked by season, altitude and shade (no daily weather).";
        this.btn.addEventListener("click", () => this.toggle());
        div.append(this.btn);
        return div;
      },
      onRemove: () => this.btn.parentElement?.remove(),
    };
  }

  private paint() {
    if (!this.map.getLayer(FILL)) return;
    const v = ["to-number", ["get", `r${this.month}`], 0];
    this.map.setPaintProperty(FILL, "fill-color", ["interpolate", ["linear"], v, ...SCORE_STOPS.flat()] as unknown as maplibregl.ExpressionSpecification);
    this.map.setPaintProperty(FILL, "fill-opacity", ["interpolate", ["linear"], v, 0, 0.62, 50, 0.72, 80, 0.9, 100, 0.95] as unknown as maplibregl.ExpressionSpecification);
  }

  private toggle() {
    this.on = !this.on;
    this.btn.setAttribute("aria-pressed", String(this.on));
    this.btn.classList.toggle("on", this.on);
    this.note.hidden = !this.on;
    if (this.on && !this.loaded) {
      this.loaded = true;
      this.map.addSource(SRC, { type: "vector", url: `pmtiles://${this.url}` });
      const before = ["lab-pine15-fill", "finds-dot"].find((id) => this.map.getLayer(id));
      this.map.addLayer({ id: FILL, type: "fill", source: SRC, "source-layer": "areas", paint: { "fill-color": "#000" } }, before);
      this.paint();
    }
    if (this.map.getLayer(FILL)) this.map.setLayoutProperty(FILL, "visibility", this.on ? "visible" : "none");
  }
}
