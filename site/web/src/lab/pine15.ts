// LAB ONLY (experiment 04): the squares that "15% forest if mostly pine" would ADD to the map's forest
// (data/lab_pine15.geojson, made by experiments/04-forest-edges/export_pine15.py). A map button shows
// them in bright blue, with a short note. Not part of the score; nothing here goes live.
import * as maplibregl from "maplibre-gl";

const SRC = "lab-pine15", FILL = "lab-pine15-fill", LINE = "lab-pine15-line";

export class Pine15 {
  private on = false;
  private loaded = false;
  private btn!: HTMLButtonElement;
  private note: HTMLElement;

  constructor(private map: maplibregl.Map, private dataUrl: string, stage: HTMLElement) {
    this.note = document.createElement("div");
    this.note.className = "pine15-note";
    this.note.hidden = true;
    this.note.innerHTML = `<strong><span class="pine15-sw" aria-hidden="true"></span>Lab test: new pine squares</strong>
      <span>15–25% forest, mostly pine. The live map leaves these out (it needs 25%). 3,040 squares, 190 km². Not live.</span>`;
    stage.append(this.note);
  }

  control(): maplibregl.IControl {
    return {
      onAdd: () => {
        const div = document.createElement("div");
        div.className = "maplibregl-ctrl maplibregl-ctrl-group";
        this.btn = document.createElement("button");
        this.btn.type = "button";
        this.btn.className = "ctrl-finds ctrl-pine15";
        this.btn.innerHTML = `<span class="pine15-sw" aria-hidden="true"></span><span>Pine 15%</span>`;
        this.btn.setAttribute("aria-pressed", "false");
        this.btn.dataset.tip = "Lab test: squares the 15% pine rule would add to the forest.";
        this.btn.addEventListener("click", () => this.toggle());
        div.append(this.btn);
        return div;
      },
      onRemove: () => this.btn.parentElement?.remove(),
    };
  }

  private toggle() {
    this.on = !this.on;
    this.btn.setAttribute("aria-pressed", String(this.on));
    this.btn.classList.toggle("on", this.on);
    this.note.hidden = !this.on;
    if (this.on && !this.loaded) {
      this.loaded = true;
      this.map.addSource(SRC, { type: "geojson", data: new URL(this.dataUrl, location.href).href });   // full address: the map worker lives in vendor/
      const before = this.map.getLayer("finds-dot") ? "finds-dot" : undefined;
      this.map.addLayer({ id: FILL, type: "fill", source: SRC,
        paint: { "fill-color": "#00b4d8", "fill-opacity": ["interpolate", ["linear"], ["zoom"], 8, 0.85, 13, 0.45] } }, before);
      this.map.addLayer({ id: LINE, type: "line", source: SRC, minzoom: 12,
        paint: { "line-color": "#0077b6", "line-width": 1.2 } }, before);
    }
    for (const id of [FILL, LINE]) if (this.map.getLayer(id)) this.map.setLayoutProperty(id, "visibility", this.on ? "visible" : "none");
  }
}
