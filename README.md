# Rex-Omni Object Detection Pipeline

Rex-Omni alapú objektum detektálási rendszer gyári összeszerelő állomásokhoz és általános objektum felismeréshez.

## 📁 Scriptek Áttekintése

### 🎥 Kamera Szerverek

#### `camera_server.py`
Flask alapú HTTP szerver amely a **laptop kameráját** streameli SSH szerver számára.

**Használat:**
```bash
# Laptop-on futtatni:
python camera_server.py
```

**Funkciók:**
- `/video` - Multipart MJPEG stream (folyamatos videó)
- `/snapshot` - Egyetlen JPEG frame (jobb VPN/instabil kapcsolatokhoz)
- `/test` - Böngészős preview
- Alapértelmezett port: **5001**

**Mikor használd:**
- Amikor a szerver gépen nincs kamera
- SSH/VPN kapcsolaton keresztül szeretnél kamerát használni
- Remote munkavégzéshez

---

### 🤖 Detekciós Pipeline-ok

#### `factory_assembly_pipeline.py` ⭐ (Batch feldolgozás)
**Batch képfeldolgozás** - több kép egymás utáni feldolgozása.

**Használat:**
```bash
from factory_assembly_pipeline import FactoryAssemblyPipeline

pipeline = FactoryAssemblyPipeline(
    model_path="IDEA-Research/Rex-Omni",
    output_dir="pipeline_results"
)

# Egy kép feldolgozása
result = pipeline.process_single_image("image.jpg")

# Mappa feldolgozása
results = pipeline.process_directory("images/")
```

**Jellemzők:**
- GPU gyorsítás (`attn_implementation="sdpa"`, `device_map="auto"`)
- Vizualizációk mentése
- JSON eredmények exportálása
- Batch statisztikák

**Mikor használd:**
- Több kép feldolgozásához egyszerre
- Offline képek elemzéséhez
- Amikor nincs szükség élő kamerára

---

#### `run_on_images.py` (Egyszerű wrapper)
Egyszerű script amely a `factory_assembly_pipeline.py`-t használja az **images/** mappa feldolgozásához.

**Használat:**
```bash
python run_on_images.py
```

**Mit csinál:**
1. Betölti az `images/` mappát
2. Feldolgozza az összes képet
3. Eredményeket menti `pipeline_results/` mappába

**Mikor használd:**
- Gyors teszteléshez
- Ha már van egy images/ mappád képekkel

---

#### `headless_camera_detection.py` ⭐ (SSH/Headless)
**SSH-kompatibilis** élő kamera detekció - **NINCS GUI**, parancssori vezérlés.

**Használat:**
```bash
# Szerverről (SSH-ban):
python headless_camera_detection.py --camera http://10.8.0.3:5001

# Vezérlés:
# [ENTER] - Snapshot készítése és detektálás
# [q] + [ENTER] - Kilépés
```

**Jellemzők:**
- HTTP snapshot alapú (nem folyamatos stream)
- Nincs OpenCV ablak (GUI-less)
- SSH-on keresztül működik
- Manuális trigger (ENTER gomb)
- Snapshot-ok mentése: `live_detections/`

**Mikor használd:**
- SSH kapcsolaton keresztüli munkavégzéshez ⭐
- Amikor nincs GUI (headless szerver)
- VPN/instabil kapcsolatoknál
- Remote kamera használatához

**Kimenet:**
- `snapshot_XXXX_YYYYMMDD_HHMMSS_original.jpg` - Eredeti kép
- `snapshot_XXXX_YYYYMMDD_HHMMSS_detected.jpg` - Vizualizált detekciók
- `snapshot_XXXX_YYYYMMDD_HHMMSS_result.json` - JSON eredmények

---

#### `live_video_detection.py` (GUI preview)
**GUI-s** élő videó detekció - OpenCV ablakkal, vizuális preview.

**Használat:**
```bash
# Lokális kamera
python live_video_detection.py --camera 0

# Remote stream
python live_video_detection.py --stream http://10.8.0.3:5001/video
```

**Jellemzők:**
- OpenCV ablak élő preview-val
- SPACE gomb - snapshot és detektálás
- Q gomb - kilépés
- Folyamatos videó stream

**Mikor használd:**
- Amikor van GUI (nem SSH)
- Lokális gépen futtatáshoz
- Vizuális feedback kell

**FIGYELEM:**
- ❌ Nem működik SSH-n (nincs X11 display)
- ✅ Lokális gépre vagy grafikus desktop környezethez

---

#### `remote_camera_detection.py` (HTTP Frame Grabber + GUI)
**HTTP alapú** frame grabber GUI preview-val - VPN/WiFi kapcsolatokhoz.

**Használat:**
```bash
python remote_camera_detection.py --camera http://10.8.0.3:5001 --fps 5
```

**Jellemzők:**
- HTTP snapshot alapú (nem multipart stream)
- OpenCV preview ablak
- Alacsonyabb FPS (3-5) instabil kapcsolatokhoz
- SPACE - snapshot és detektálás

**Különbség a `live_video_detection.py`-tól:**
- Snapshot-ok helyett stream (megbízhatóbb VPN-en)
- Alacsonyabb FPS beállítható

**Mikor használd:**
- VPN/WiFi kapcsolatoknál ahol a stream akadozik
- GUI elérhető de instabil a hálózat

---

### 🔧 Segédeszközök

#### `factory_assembly_categories.py`
**Kategória definíciók** - objektum típusok listája.

**Tartalom:**
- `COMMON_ASSEMBLY_OBJECTS` - 40+ kategória (gyári + általános objektumok)
- Szerszámok: screwdriver, wrench, pliers, hammer, ...
- Alkatrészek: screw, bolt, PCB, cable, sensor, ...
- Általános: person, face, phone, book, air conditioner, ...

**Hogyan bővítsd:**
```python
# factory_assembly_categories.py
COMMON_ASSEMBLY_OBJECTS = [
    "laptop", "tablet",
    
    # Add új kategóriák
    "új_objektum_1", "új_objektum_2",
]
```

---

#### `test_camera_connection.py`
**Kapcsolat tesztelő** - ellenőrzi hogy elérhető-e a camera server.

**Használat:**
```bash
python test_camera_connection.py http://10.8.0.3:5001/video
```

**Mit teszt:**
1. Base URL elérhetőség
2. Stream endpoint működés
3. Adat fogadás

**Mikor használd:**
- Hibakereséshez
- Hálózati kapcsolat ellenőrzéséhez
- Telepítés után teszteléshez

---

## 🚀 Gyorsindítás

### 1. Lokális képek feldolgozása
```bash
# Képeket rakd az images/ mappába
python run_on_images.py

# Eredmények: pipeline_results/
```

### 2. Remote kamera SSH-n keresztül
```bash
# 1. Laptop-on indítsd a camera server-t:
python camera_server.py

# 2. Szerverről (SSH):
python headless_camera_detection.py --camera http://10.8.0.3:5001
# [ENTER] - snapshot készítése
```

### 3. Lokális kamera GUI-val
```bash
python live_video_detection.py --camera 0
# [SPACE] - detektálás
```

---

## 📊 Kimenet Formátumok

### Vizualizált képek
- Detektált objektumok bounding box-okkal
- Címkék színkódolva
- Formátum: JPEG

### JSON eredmények
```json
{
  "timestamp": "20260113_175033",
  "processing_time": 8.49,
  "found_objects": {
    "person": [{"type": "box", "coords": [x1, y1, x2, y2]}],
    "phone": [{"type": "box", "coords": [x1, y1, x2, y2]}],
    "air conditioning": [{"type": "box", "coords": [x1, y1, x2, y2]}]
  },
  "summary": {
    "total_object_types": 10,
    "total_objects": 11
  }
}
```

---

## ⚙️ GPU Beállítások

Minden pipeline használja:
- `attn_implementation="sdpa"` - GPU-optimalizált attention
- `device_map="auto"` - Automatikus GPU allokáció

**Sebesség:**
- CPU: ~172s / kép
- GPU (sdpa): ~6-8s / kép

---

## 🔄 Workflow Összefoglaló

```
┌─────────────────────┐
│   KÉPEK FORRÁSA     │
└─────────┬───────────┘
          │
    ┌─────┴─────────────────────────────┐
    │                                   │
    ▼                                   ▼
┌─────────────┐                  ┌──────────────┐
│  BATCH      │                  │  ÉLŐ KAMERA  │
│  (offline)  │                  │  (live)      │
└──────┬──────┘                  └──────┬───────┘
       │                                │
       │                         ┌──────┴────────┐
       │                         │               │
       │                         ▼               ▼
       │                   ┌──────────┐    ┌──────────┐
       │                   │   SSH    │    │   GUI    │
       │                   │ headless │    │  preview │
       │                   └────┬─────┘    └────┬─────┘
       │                        │               │
       ▼                        ▼               ▼
  ┌─────────────────────────────────────────────────┐
  │     factory_assembly_pipeline.py                │
  │     (Rex-Omni + GPU processing)                 │
  └─────────────────┬───────────────────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │  EREDMÉNYEK      │
          │  - Vizualizációk │
          │  - JSON adatok   │
          └──────────────────┘
```

---

## 📝 Melyik Script-et Használjam?

| Használati Eset | Script | GUI | SSH-kompatibilis |
|----------------|--------|-----|------------------|
| Offline képek batch feldolgozása | `run_on_images.py` | ❌ | ✅ |
| SSH remote kamera | `headless_camera_detection.py` | ❌ | ✅ |
| Lokális kamera GUI-val | `live_video_detection.py` | ✅ | ❌ |
| Remote kamera instabil hálózaton (GUI) | `remote_camera_detection.py` | ✅ | ❌ |
| Camera stream a laptop-ról | `camera_server.py` | ❌ | ✅ |

---

## 🛠️ Hibaelhárítás

### "Camera server nem elérhető"
```bash
# Tesztelés:
python test_camera_connection.py http://10.8.0.3:5001/video

# Ellenőrizd:
# - Fut-e a camera_server.py a laptop-on
# - Helyes-e az IP cím (VPN IP: 10.8.0.x)
# - Nincs-e tűzfal blokkolás
```

### "OpenCV error: no display"
→ Használd a `headless_camera_detection.py`-t SSH-hoz!

### "Nincs detekció / 0 objektum"
→ Bővítsd a `factory_assembly_categories.py` kategória listát!

---

## 📚 További Dokumentáció

- [PIPELINE_USAGE.md](docs/PIPELINE_USAGE.md) - Pipeline részletes használat
- [REX_OMNI_OBJECT_DETECTION_GUIDE.md](docs/REX_OMNI_OBJECT_DETECTION_GUIDE.md) - Rex-Omni útmutató
