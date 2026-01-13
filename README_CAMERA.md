# Rex-Omni Kamerás Object Detection

Ez a dokumentáció bemutatja, hogyan használhatod a Rex-Omni modellt saját kamerával való object detection-höz.

## 📋 Előkövetelmények

### 1. Függőségek telepítése

Először telepítsd a szükséges Python csomagokat:

```bash
pip install -r requirements.txt
```

További szükséges csomagok kamerás használathoz:

```bash
pip install opencv-python
```

### 2. Rex-Omni modell letöltése

A modellt le kell tölteni a Hugging Face-ről:

```bash
# Hugging Face CLI használata (ajánlott)
pip install huggingface_hub
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni
```

Vagy Git LFS-sel:

```bash
git lfs install
git clone https://huggingface.co/IDEA-Research/Rex-Omni models/Rex-Omni
```

## 🎥 Kamerás használat

Két szkriptet készítettem:

### 1. Egyszerű verzió - Egy kép rögzítése és elemzése

A `simple_camera_demo.py` egy egyszerű példa, amely egy képet készít a kameráddal és elemzi:

```bash
python simple_camera_demo.py
```

**Használat:**
1. A szkript elindítja a kamerát
2. Nyomj **SPACE**-t a kép rögzítéséhez
3. A modell elemzi a képet
4. Az eredmény megjelenik a konzolon és egy ablakban
5. Az eredmény `detection_result.jpg` néven mentésre kerül

### 2. Valós idejű verzió - Folyamatos detektálás

A `camera_detection.py` valós időben elemzi a kamera képét:

```bash
# Alapértelmezett beállítások
python camera_detection.py

# További opciók megadása
python camera_detection.py --fps 3 --categories person car dog cat
```

**Irányítás:**
- **Q**: Kilépés
- **S**: Aktuális kép mentése
- **P**: Szüneteltetés/Folytatás

**Paraméterek:**

```bash
python camera_detection.py \
  --model_path models/Rex-Omni \
  --backend transformers \
  --camera 0 \
  --fps 5 \
  --categories person car dog cat phone laptop \
  --task detection \
  --max_tokens 1024 \
  --temperature 0.0
```

| Paraméter | Leírás | Alapértelmezett |
|-----------|--------|-----------------|
| `--model_path` | Modell elérési útja | `models/Rex-Omni` |
| `--backend` | Backend típus (`transformers` vagy `vllm`) | `transformers` |
| `--camera` | Kamera forrás (0 = alapértelmezett webcam, vagy IP kamera URL) | `0` |
| `--fps` | Feldolgozási sebesség (FPS) - alacsonyabb érték = kevesebb CPU/GPU terhelés | `5` |
| `--categories` | Keresendő kategóriák (szóközzel elválasztva) | `person car dog cat phone laptop` |
| `--task` | Feladat típusa | `detection` |
| `--keypoint_type` | Kulcspont típus (ha `--task keypoint`) | `person` |
| `--max_tokens` | Maximum token szám | `1024` |
| `--temperature` | Mintavételi hőmérséklet | `0.0` |

## 🎯 Támogatott feladatok (tasks)

Rex-Omni különböző computer vision feladatokat tud végrehajtani:

### 1. Object Detection (detection)
Objektumok detektálása és lokalizálása bounding box-okkal.

```bash
python camera_detection.py --task detection --categories person car dog
```

### 2. Object Pointing (pointing)
Objektumok középpontjának meghatározása.

```bash
python camera_detection.py --task pointing --categories person
```

### 3. Keypoint Detection (keypoint)
Kulcspontok (például emberi pózok) detektálása.

```bash
python camera_detection.py --task keypoint --keypoint_type person
```

Kulcspont típusok:
- `person`: Emberi pózok (17 kulcspont)
- `animal`: Állati pózok
- `hand`: Kéz kulcspontok

### 4. OCR - Szövegfelismerés
Szöveg detektálása és felismerése.

```bash
# Bounding box formátum
python camera_detection.py --task ocr_box --categories text

# Polygon formátum (pontosabb)
python camera_detection.py --task ocr_polygon --categories text
```

## 💡 Példák különböző használati esetekre

### Emberek számlálása térfigyelő kamerával
```bash
python camera_detection.py \
  --categories person \
  --fps 2 \
  --task detection
```

### Járművek detektálása
```bash
python camera_detection.py \
  --categories car truck bus motorcycle bicycle \
  --fps 3
```

### Póz detektálás (pl. fitness app-hez)
```bash
python camera_detection.py \
  --task keypoint \
  --keypoint_type person \
  --fps 5
```

### Dokumentum szkenner (OCR)
```bash
python camera_detection.py \
  --task ocr_polygon \
  --categories text \
  --fps 2
```

### IP kamera használata
```bash
python camera_detection.py \
  --camera "rtsp://192.168.1.100:554/stream" \
  --categories person car \
  --fps 2
```

## 🔧 Teljesítmény optimalizálás

### FPS beállítás
- **Alacsony FPS (1-3)**: Lassabb eszközökhöz, kevés CPU/GPU terheléssel
- **Közepes FPS (4-6)**: Átlagos teljesítményű gépekhez
- **Magas FPS (7+)**: Erős GPU-val rendelkező gépekhez

### Backend választás
- **transformers**: Univerzális, könnyen használható, GPU vagy CPU
- **vllm**: Gyorsabb, de GPU szükséges, több memória

### Kamera felbontás
A szkript automatikusan 1280x720-ra állítja a kamerát. Ha ez túl magas:

Módosítsd a `camera_detection.py` fájlban:
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 1280 helyett
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 720 helyett
```

## 🐛 Hibaelhárítás

### Kamera nem nyílik meg
```bash
# Ellenőrizd az elérhető kamerákat
ls /dev/video*  # Linux
# vagy próbáld ki különböző indexeket: 0, 1, 2, ...
```

### Lassú feldolgozás
1. Csökkentsd az FPS-t: `--fps 2`
2. Kevesebb kategóriát adj meg
3. Csökkentsd a kamera felbontást
4. Használj GPU-t

### CUDA out of memory
1. Csökkentsd a `--max_tokens` értékét
2. Állítsd le a többi GPU-t használó programot
3. Használj kisebb batch size-t (a jelenlegi szkript 1 képet dolgoz fel egyszerre)

### Modell nem található
Ellenőrizd, hogy a modell a megfelelő helyre lett-e letöltve:
```bash
ls -la models/Rex-Omni/
```

Látnod kell: `config.json`, `model.safetensors`, stb.

## 📚 További információk

- **Hivatalos Rex-Omni dokumentáció**: https://rex-omni.github.io/
- **GitHub repo**: https://github.com/IDEA-Research/Rex-Omni
- **Hugging Face model**: https://huggingface.co/IDEA-Research/Rex-Omni
- **Tutorialok**: https://github.com/IDEA-Research/Rex-Omni/tree/master/tutorials

## 🎓 Kód példák

### Saját szkript készítése

```python
import cv2
from PIL import Image
from rex_omni.wrapper import RexOmniWrapper

# Modell betöltése
model = RexOmniWrapper(
    model_path="models/Rex-Omni",
    backend="transformers",
    max_tokens=1024,
    temperature=0.0
)

# Kamera megnyitása
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# OpenCV BGR -> PIL RGB
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(rgb_frame)

# Detektálás
result = model.inference(
    images=pil_image,
    task="detection",
    categories=["person", "car"]
)

# Eredmény feldolgozása
if result:
    predictions = result[0]['extracted_predictions']
    print(f"Detektált objektumok: {predictions}")

cap.release()
```

## ⚡ Gyors kezdés

1. **Telepítés**:
```bash
pip install -r requirements.txt
pip install opencv-python
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni
```

2. **Egyszerű teszt**:
```bash
python simple_camera_demo.py
```

3. **Valós idejű detektálás**:
```bash
python camera_detection.py
```

Kész vagy! 🚀
