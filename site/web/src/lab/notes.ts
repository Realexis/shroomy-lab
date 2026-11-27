// LAB ONLY: one column at the top left of the map for the lab layers' notes, so they stack.
export function labNotes(stage: HTMLElement): HTMLElement {
  let box = stage.querySelector<HTMLElement>(".lab-notes");
  if (!box) {
    box = document.createElement("div");
    box.className = "lab-notes";
    stage.append(box);
  }
  return box;
}
