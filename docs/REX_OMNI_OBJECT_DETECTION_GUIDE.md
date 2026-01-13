# Rex-Omni Object Detection - Teljes Útmutató

## 📋 Mi a Rex-Omni?

A **Rex-Omni** egy 3 milliárd paraméteres multimodális nagy nyelvi modell (MLLM) az IDEA-Research csapatától, amely objektum detektálást és számos más látási feladatot hajt végre egyszerű "next-token prediction" problemaként.

- **Modell méret**: 3B paraméter
- **Háttérszoftver**: Transformers (vagy vLLM gyorsabb inference-hez)
- **Alapmodell**: Qwen 2.5-VL
- **Támogatott feladatok**: Detection, Pointing, Keypoint, OCR, Visual Prompting, GUI Grounding stb.

### 🌟 OPEN-VOCABULARY Képesség!

**FONTOS**: A Rex-Omni **NEM csak** előre tanított kategóriákra korlátozódik!

✅ **BÁRMILYEN természetes nyelvű kategóriát** megadhatsz:
- Alapvető tárgyak: "hammer", "screwdriver", "wrench", "cup", "phone"
- Színekkel: "red car", "yellow flower", "blue umbrella"
- Leíró kategóriák: "screwdriver with red handle", "person wearing glasses"
- Specifikus tárgyak: "adjustable wrench", "phillips screwdriver", "laptop keyboard"
- Összetett kifejezések: "boys holding microphone", "the guitar in someone's hand"

⚠️ **Korlátok**:
- A felismerés minősége függ a training adatoktól
- Angol nyelv működik a legjobban
- Nagyon speciális/ritka tárgyak gyengébb felismerés
- Magyar nyelv részben támogatott, de angol javasolt

---

## 🎯 Támogatott Feladatok

### 1. **Object Detection** (Objektum detektálás) ⭐ 
Objektumok felismerése és bounding box-szal való lokalizálása
- **Bemenet**: Kép + Kategóriák listája
- **Kimenet**: Bounding boxok `[x0, y0, x1, y1]` formában
- **Alkalmazások**: COCO kategóriák, egyedi objektumok, többnyelvű szövegek

### 2. **Pointing** (Mutatás)
Pont-precíz lokalizálása megadott objektumoknak
- **Kimenet**: Pontok `[x, y]` formában

### 3. **Visual Prompting** (Vizuális prompt)
Hasonló objektumok keresése referencia alapján
- **Bemenet**: Referencia bounding boxok
- **Alkalmazás**: Hasonló tárgyak megtalálása képen

### 4. **Keypoint Detection** (Kulcspont detektálás)
Emberi póz vagy állati testalkatrészek detektálása
- **Támogatott típusok**: "person", "hand", "animal"
- **Alkalmazások**: Pose estimation, mozgáselemzés

### 5. **OCR** (Optikai karakterfelismerés)
Szöveg felismerése Box vagy Polygon formátumban
- **OCR Box**: Szavak/szövegvonalak dobozos formában
- **OCR Polygon**: Szöveg poligon formátumban

### 6. **GUI Detection / Pointing** (GUI elemek)
GUI elemek detektálása és mutatása felhasználói felületeknél

---

## 🚀 Gyors Kezdés

### Alapvető Objektum Detektálás

```python
from PIL import Image
from rex_omni import RexOmniWrapper, RexOmniVisualize

# 1) Wrapper inicializálása
rex = RexOmniWrapper(
    model_path="IDEA-Research/Rex-Omni",   # HF repo vagy local path
    backend="transformers",                 # vagy "vllm" gyors inference-hez
    max_tokens=2048,
    temperature=0.0,                        # Determinisztikus
    top_p=0.05,
    top_k=1,
    repetition_penalty=1.05,
)

# 2) Kép betöltése
image = Image.open("path/to/image.jpg").convert("RGB")

# 3) Kategóriák megadása
categories = [
    "person", "car", "dog", "cat", "laptop", "phone"
]

# 4) Detektálás futtatása
results = rex.inference(
    images=image, 
    task="detection", 
    categories=categories
)

# 5) Eredmények feldolgozása
result = results[0]  # Egy képhez egy eredmény
predictions = result["extracted_predictions"]
# Kimenet: {'person': [...], 'car': [...], ...}

# 6) Vizualizálás
vis_image = RexOmniVisualize(
    image=image,
    predictions=predictions,
    font_size=20,
    draw_width=5,
    show_labels=True
)
vis_image.save("output.jpg")
```

---

## 📊 RexOmniWrapper Paraméterek

### Inicializálás Paraméterei

| Paraméter | Típus | Leírás | Alapérték |
|-----------|-------|--------|-----------|
| `model_path` | str | HF repo ID vagy local path | "IDEA-Research/Rex-Omni" |
| `backend` | str | "transformers" vagy "vllm" | "transformers" |
| `max_tokens` | int | Max generált tokenek | 2048 |
| `temperature` | float | Sampling hőmérséklet (0=determinisztikus) | 0.0 |
| `top_p` | float | Nucleus sampling | 0.05 |
| `top_k` | int | Top-k sampling | 1 |
| `repetition_penalty` | float | Ismétlés büntetés | 1.05 |

### Inference Paraméterei

```python
results = rex.inference(
    images=image_or_list,      # PIL.Image vagy lista
    task="detection",          # Task típus
    categories=["person"],     # Keresendő kategóriák
    keypoint_type=None,        # "person", "hand", "animal" (keypoint taskhoz)
    visual_prompt_boxes=None,  # [[x0,y0,x1,y1],...] visual prompting-hez
)
```

**Támogatott task értékek:**
- `"detection"` - Objektum detektálás
- `"pointing"` - Pont lokalizálás
- `"visual_prompting"` - Vizuális prompt
- `"keypoint"` - Kulcspont detektálás
- `"ocr_box"` - OCR dobozokkal
- `"ocr_polygon"` - OCR poligonokkal
- `"gui_grounding"` - GUI detektálás
- `"gui_pointing"` - GUI mutatás

---

## 📈 Output Format

### Detection Eredmény Struktúra

```python
result = {
    "success": True,
    "raw_output": "...",  # LLM nyers kimenete
    "extracted_predictions": {
        "person": [
            {"type": "box", "coords": [x0, y0, x1, y1]},
            {"type": "box", "coords": [x0, y0, x1, y1]},
        ],
        "car": [
            {"type": "box", "coords": [x0, y0, x1, y1]},
        ],
    }
}
```

### Pointing Eredmény Struktúra

```python
"extracted_predictions": {
    "person": [
        {"type": "point", "coords": [x, y]},
    ]
}
```

---

## 💻 Backenyek Összehasonlítása

| Szempont | Transformers | vLLM |
|---------|-------------|------|
| Felhasználás | Egyszerű | Összetett |
| Sebességség | Közepes | ✅ Gyors |
| Memória | Normál | Optimalizált |
| Batch inference | Támogatott | ✅ Jó |
| Beállítás | Egyszerű | Sok opció |

**Ajánlás**: 
- Kezdőknél: `backend="transformers"`
- Éles rendszer/gyors inference: `backend="vllm"`

---

## 🎬 Kamerás Real-Time Detektálás

Az `interactive_camera_demo.py` segítségével valós időben lehet detektálni:

```bash
# Teljes COCO kategóriákkal
python interactive_camera_demo.py

# Egyedi kategóriákkal
python camera_detection.py --categories person car dog --fps 2
```

### Kamera Demó Jellemzői
- ✅ 2 FPS feldolgozás (8GB RAM-hoz optimalizált)
- ✅ 80 COCO kategória automatikus felismerése
- ✅ Eredmények mentése `detections/` mappába
- ✅ Console output az eredményekkel
- ✅ Ctrl+C leállítás

---

## 🔧 Advanced: Batch Inference

```python
from PIL import Image
from rex_omni import RexOmniWrapper

# Több kép feldolgozása egyszerre
images = [
    Image.open(f"image_{i}.jpg").convert("RGB")
    for i in range(5)
]

rex = RexOmniWrapper(model_path="IDEA-Research/Rex-Omni", backend="vllm")

# Batch inference
results = rex.inference(
    images=images,
    task="detection",
    categories=["person", "car", "dog"]
)

# Eredmények feldolgozása
for i, result in enumerate(results):
    print(f"Image {i}: {result['extracted_predictions']}")
```

---

## 📁 Repo Struktúra

```
rex-omni/                              # ComfyUI integráció (CustomNode)
├── interactive_camera_demo.py          # ⭐ Kamera demo - 80 COCO kategória
├── camera_detection.py                 # Kamerás detektálás paraméteres
├── simple_camera_demo.py               # Egyetlen frame capture

Rex-Omni/                              # ⭐ Eredeti repo
├── tutorials/
│   ├── detection_example/
│   │   ├── detection_example.py        # Alapvető detektálás
│   │   ├── referring_example.py        # Object referring
│   │   ├── gui_grounding_example.py    # GUI elemek
│   │   └── test_images/                # Teszt képek
│   ├── pointing_example/
│   ├── keypointing_example/
│   ├── ocr_example/
│   └── visual_prompting_example/
├── applications/                       # Rex-Omni + SAM, Grounding Data Engine
├── finetuning/                         # Fine-tuning guide
├── evaluation/                         # Evaluation script-ek
└── app.py                             # Gradio demo
```

---

## 🎓 Oktatási Anyagok

Az eredeti repóban:
- **Python scriptlek**: `tutorials/*/` mappákban
- **Jupyter Notebookok**: `*_full_notebook.ipynb` vagy `*_full_tutorial.ipynb`
- **Gradio Demo**: `python app.py`

---

## 🛠️ Troubleshooting

### Memória problémák (8GB RAM)
```python
# Csökkentett beállítások
rex = RexOmniWrapper(
    model_path="IDEA-Research/Rex-Omni",
    backend="transformers",
    max_tokens=256,  # Csökkentve 2048-ről
    # device_map=None,  # macOS-n szükséges
)
```

### macOS: Flash Attention 2 hiba
```python
# Eagerly attention-t kell használni
rex = RexOmniWrapper(
    model_path="...",
    backend="transformers",
    # attn_implementation="eager",  # macOS-n szükséges
)
```

### GPU nincs: CPU fallback
```python
rex = RexOmniWrapper(
    model_path="IDEA-Research/Rex-Omni",
    backend="transformers",
    device="cpu"  # Lassú, de működik
)
```

---

## 📚 További Linkek

- **Hugging Face Repo**: https://huggingface.co/IDEA-Research/Rex-Omni
- **Hugging Face Demo**: https://huggingface.co/spaces/Mountchicken/Rex-Omni
- **ArXiv Paper**: https://arxiv.org/abs/2510.12798
- **GitHub**: https://github.com/IDEA-Research/Rex-Omni
- **Website**: https://rex-omni.github.io/

---

## 💡 Praktikus Példák

### 1️⃣ Egyedi Kategóriák Detektálása

```python
categories = ["red car", "person with blue hat", "wooden chair"]
results = rex.inference(images=image, task="detection", categories=categories)
```

### 2️⃣ Pontosan Megadott Objektumok

```python
categories = ["tall building", "green tree"]
results = rex.inference(images=image, task="pointing", categories=categories)
```

### 3️⃣ Emberi Póz Detektálása

```python
results = rex.inference(
    images=image,
    task="keypoint",
    categories=["person"],
    keypoint_type="person"  # nose, eyes, ears, shoulders, etc.
)
```

### 4️⃣ Szöveg Felismerése

```python
results = rex.inference(
    images=image,
    task="ocr_box",
    categories=["text"]  # Összes szöveg
)
# Output: szövegdobozok koordinátái
```

### 5️⃣ Szerszámok Felismerése Asztalon 🔧

```python
# OPEN-VOCABULARY: bármilyen szerszám kategória!
tool_categories = [
    # Alapvető szerszámok
    "hammer", "screwdriver", "wrench", "pliers",
    
    # Specifikus típusok
    "flat screwdriver", "phillips screwdriver",
    "adjustable wrench",
    
    # Színekkel
    "red screwdriver", "yellow hammer",
    
    # Leíró kategóriák
    "screwdriver with red handle",
    "large adjustable wrench"
]

image = Image.open("tools_table.jpg").convert("RGB")
results = rex.inference(
    images=image,
    task="detection",
    categories=tool_categories
)

# Eredmények feldolgozása
for tool, detections in results[0]['extracted_predictions'].items():
    if detections:
        print(f"✓ {tool}: {len(detections)} darab")
```

**Tipp**: Adj meg több variációt ugyanarra a tárgyra:
- `"wrench"` + `"adjustable wrench"` + `"metal wrench"`
- `"screwdriver"` + `"red screwdriver"` + `"flat screwdriver"`

---

## ✨ Összefoglalás

| Funkció | Helyzet |
|---------|--------|
| **Objektum detektálás** | ✅ Kiváló, 80 COCO kategória |
| **Kamera support** | ✅ Real-time 2 FPS-en |
| **Keypoint detektálás** | ✅ Person, hand, animal |
| **OCR** | ✅ Box és polygon formátum |
| **Gyorsság** | ⚠️ 1-2 FPS CPU-n, 5-10 FPS GPU-n |
| **Memória** | ⚠️ 8GB minimális |
| **macOS támogatás** | ✅ Eager attention-nel |

