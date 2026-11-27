# Back-test: which mushrooms count (draft for Real's OK, 27 Nov 2026)

"Usable" = exact spot (within 500 m) + exact day + 1 Oct–30 Apr + seasons 2022–2026 (the years we have the live map's weather for).
"Target species" = the map's own species list (`site/config/species.yaml`).

## KEEP: main group (grow in the ground with trees, or are target species) — 45 usable finds

| Genus | Usable | Why |
|---|---|---|
| Suillus | 8 | Target species. Grows with pine. |
| Lactarius | 8 | Target (L. deliciosus). Grows with pine / oak. |
| Pisolithus | 4 | Grows with pine (earthball-like, in the ground). |
| Russula | 3 | Target (R. delica). Grows with trees. |
| Hygrophorus | 3 | Grows with trees. |
| Rhizopogon | 3 | Grows with pine (underground). |
| Inocybe | 2 | Grows with trees. |
| Clavulina | 2 | Grows with trees (coral-like). |
| Clavariadelphus | 2 | Probably grows with trees (less sure). |
| Morchella | 2 | Target species (morels). Spring. |
| Laccaria | 1 | Grows with trees. |
| Tricholoma | 1 | Target (T. caligatum). Grows with trees. |
| Ramaria | 1 | Most grow with trees (coral fungi). |
| Cortinarius (Telamonia) | 1 | Grows with trees. |
| Chroogomphus | 1 | Grows with pine. |
| Thelephora | 1 | Grows with trees. |
| Xerocomellus | 1 | Bolete. Grows with trees. |
| Astraeus | 1 | Grows with trees (earthstar-like). |
| Amanita, Scleroderma, Leccinellum, Sarcodon, Gyrodon, Hygrocybe, Pseudosperma, Sebacina | 0 | Same way of growing, but no usable find in 2022–26. |

## DROP

| Group | Genera (usable finds) | Why |
|---|---|---|
| **On wood** (brackets, crusts, jelly fungi) | Stereum 7, Tulasnella 5, Sistotrema 3, Crepidotus 3, Phellinus 3, Gymnopilus 2, Inocutis 2, Auricularia 2, Dacrymyces 2, Pleurotus 2, Schizophyllum 2, Botryobasidium 2, Coniophora 2, Rhizoctonia 2, Laetiporus, Ganoderma, Fomes, Fomitiporia, Fuscoporia, Porodaedalea, Armillaria, Omphalotus, Trametes, Exidia, Tremella, Phaeotremella, Calocera, Chondrostereum, Byssomerulius, Sistotremastrum, Elfvingia, Scutellinia, Sarcoscypha (1 each) | Live on dead or living wood; they follow the wood's water, not the soil's. |
| **Ground decomposers** (not with trees, not target) | Agaricus 10, Mycena 9, Lycoperdon 8, Volvopluteus 6, Candolleomyces 6, Battarrea 3, Coprinus 3, Agrocybe 3, Dissingia 3, Colus 2, Collybia 2, Lepiota 2, Psathyrella 2, Tulostoma 2, and others with 1 each | Feed on dead leaves, soil or grass, often in fields, parks and gardens, not only forest. Left out of the main test; shown as a second check. |
| **Dung** | Bolbitius 1 | Grows on dung or rich grass. |
| **Name too vague** | "Agaricales" 19, "Agaricomycetes" 9, "Pezizales" 3, "Lycoperdaceae" 3, "Boletales" 2, and 9 more family/order names | No genus, so we cannot tell how it grows. |
| **Not sure how it grows** | Reddellomyces 1, Nolanea (Entoloma) 1 | Left out rather than guess. |
| **Lichens, moulds, rusts, tiny fungi** | (1,756 records: lichens 1,451, other fungi 139, not named 166) | Already outside the "mushroom" group. |

## Target species on their own (side result) — 12 usable finds: LOW confidence
Suillus 8 · Lactarius deliciosus 2 · Morchella 2 · L. sanguifluus 0 · Russula delica 0 · Tricholoma caligatum 0.

## Season check (all years, any location accuracy)
- Main group by month (Jan→Dec): 20 · 9 · 7 · 6 · 1 · 0 · 0 · 1 · 4 · 16 · 20 · 21 → **one season, Oct–Jan. No clear spring peak.**
- Spring finds (Mar–May): **Morchella** (6 of its 7 records are Feb–May: the real spring one), *Lactarius deliciosus* (2: Mar, Apr), *Russula* (2), *Chroogomphus rutilus*, *Ramaria*, *Clavulina*, *Laccaria laccata*, *Leccinellum lepidum*, *Lactarius atlanticus* (1 each).
- The April 2023 cluster in the preview was mostly **wood fungi (4) and vague names (4)**; only 2 of 10 were tree-partner mushrooms (*Lactarius deliciosus*, *Ramaria*).
