# 📦 Rex-Omni Kamerás Object Detection - Teljes Csomag

## 🎯 Mit készítettem neked?

Egy **teljes kamerás object detection rendszert** a Rex-Omni modell alapján, amely képes:
- ✅ Valós időben detektálni objektumokat webkameráról vagy IP kameráról
- ✅ Különböző feladatokat végrehajtani (detection, keypoint, OCR, stb.)
- ✅ Interaktívan váltani kategóriák között
- ✅ Menteni és exportálni az eredményeket

---

## 📂 Létrehozott fájlok

### 🎥 Főbb szkriptek

#### 1. `simple_camera_demo.py` ⭐ KEZDŐKNEK
**Mit csinál?**
- Megnyitja a kamerát
- SPACE-re készít egy képet
- Elemzi az objektumokat
- Megjeleníti és menti az eredményt

**Használat:**
```bash
python simple_camera_demo.py
```

**Mikor használd?**
- Első kipróbáláskor
- Gyors teszteléshez
- Amikor csak egy képet akarsz elemezni

---

#### 2. `camera_detection.py` ⭐ HALADÓKNAK
**Mit csinál?**
- Folyamatos real-time detektálás
- Teljes paraméter kontroll
- Állítható FPS és kategóriák
- Mentés, szünet funkciók

**Használat:**
```bash
# Alapértelmezett
python camera_detection.py

# Testreszabott
python camera_detection.py \
  --categories person car dog \
  --fps 5 \
  --task detection
```

**Paraméterek:**
- `--categories`: Keresendő objektumok (pl. person car dog)
- `--fps`: Feldolgozási sebesség (1-10)
- `--task`: Feladat típus (detection, keypoint, ocr_box, stb.)
- `--camera`: Kamera forrás (0=default, vagy URL)
- `--backend`: transformers vagy vllm
- `--max_tokens`: Max token szám
- `--temperature`: Mintavételi hőmérséklet

**Billentyűk:**
- `Q`: Kilépés
- `S`: Kép mentése
- `P`: Szünet/folytatás

**Mikor használd?**
- Amikor pontosan tudod mit akarsz
- Egyedi beállításokhoz
- Parancssori futtatáshoz

---

#### 3. `interactive_camera_demo.py` ⭐⭐⭐ AJÁNLOTT
**Mit csinál?**
- Interaktív real-time detektálás
- 7 előre beállított kategória preset
- Futás közben váltható beállítások
- Vizuális információs panel

**Használat:**
```bash
python interactive_camera_demo.py
```

**Billentyűk:**
- `1-7`: Kategória preset váltás
  - 1: Emberek
  - 2: Járművek
  - 3: Állatok
  - 4: Elektronika
  - 5: Bútorok
  - 6: Konyha
  - 7: Minden (80 kategória)
- `Q`: Kilépés
- `S`: Kép mentése
- `P`: Szünet/folytatás
- `H`: Súgó be/ki

**Mikor használd?**
- **LEGJOBB VÁLASZTÁS KEZDÉSNEK!**
- Amikor kísérletezni akarsz
- Amikor nem tudod előre mit fogsz keresni
- Demo bemutatásokhoz

---

### 📚 Dokumentáció

#### `README_CAMERA.md` - Magyar útmutató
**Tartalom:**
- Részletes telepítési útmutató
- Minden funkció leírása
- Példák használati esetekre
- Teljesítmény optimalizálás
- Hibaelhárítás
- Kód példák

#### `QUICKSTART.md` - Gyors összefoglaló
**Tartalom:**
- Gyors áttekintés
- Melyik szkriptet válasszam?
- Példa parancsok
- Gyakori paraméterek
- Problémamegoldás

#### `README.md` - Frissített fő dokumentáció
**Módosítás:**
- Hozzáadtam a kamerás használat szekciót
- Linkek az új funkciókhoz

---

### 🛠️ Segédeszközök

#### `check_system.py` - Rendszer ellenőrző
**Mit csinál?**
- Ellenőrzi a Python verziót
- Ellenőrzi a telepített csomagokat
- Ellenőrzi a Rex-Omni modellt
- Teszteli a kamerát
- Ellenőrzi a GPU-t
- Ellenőrzi a szkripteket

**Használat:**
```bash
python check_system.py
```

**Kimenet példa:**
```
✓ Python verzió: OK
✓ Python csomagok: OK
✓ Rex-Omni modell: OK
✓ Kamera: OK
⚠ GPU: Nem elérhető (CPU mód)
✓ Szkriptek: OK

🎉 MINDEN RENDBEN!
```

#### `setup_camera.sh` - Telepítő script
**Mit csinál?**
- Ellenőrzi a Pythont
- Opcionálisan létrehoz virtual environment-et
- Telepíti a függőségeket
- Segít a modell letöltésében

**Használat:**
```bash
./setup_camera.sh
```

---

## 🚀 Gyors Start Útmutató

### 1. Telepítés (3 perc)

```bash
# Opció A: Automatikus telepítés
./setup_camera.sh

# Opció B: Manuális telepítés
pip install -r requirements.txt
pip install opencv-python
```

### 2. Modell letöltése (~5-10 perc, egyszer kell)

```bash
# Hugging Face CLI telepítése (ha nincs meg)
pip install huggingface_hub

# Modell letöltése (kb. 6 GB)
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni
```

### 3. Rendszer ellenőrzése (30 másodperc)

```bash
python check_system.py
```

Ha minden zöld ✓, akkor készen állsz!

### 4. Első futtatás (1 perc)

```bash
# Interaktív mód (ajánlott)
python interactive_camera_demo.py

# Vagy egyszerű demo
python simple_camera_demo.py
```

---

## 💡 Példák Különböző Használati Esetekre

### 🏢 Térfigyelés (emberek számlálása)
```bash
python camera_detection.py --categories person --fps 2
```

### 🚗 Forgalomfigyelés
```bash
python camera_detection.py \
  --categories car truck bus motorcycle bicycle \
  --fps 3
```

### 🏋️ Póz detektálás (fitness app)
```bash
python camera_detection.py \
  --task keypoint \
  --keypoint_type person \
  --fps 5
```

### 📄 OCR (dokumentum szkenner)
```bash
python camera_detection.py \
  --task ocr_polygon \
  --categories text \
  --fps 2
```

### 📹 IP kamera
```bash
python camera_detection.py \
  --camera "rtsp://192.168.1.100:554/stream" \
  --categories person \
  --fps 2
```

### 🐶 Háziállat figyelő
```bash
python camera_detection.py \
  --categories dog cat bird \
  --fps 3
```

### 📱 Asztali tárgyak detektálása
```bash
python camera_detection.py \
  --categories phone laptop mouse keyboard cup bottle \
  --fps 4
```

---

## 🎯 Támogatott Feladatok (Tasks)

### 1. Object Detection (`detection`)
Objektumok detektálása bounding box-okkal.
```bash
python camera_detection.py --task detection --categories person car
```

### 2. Object Pointing (`pointing`)
Objektumok középpontjának meghatározása.
```bash
python camera_detection.py --task pointing --categories person
```

### 3. Keypoint Detection (`keypoint`)
Kulcspontok detektálása (pózok).
```bash
python camera_detection.py --task keypoint --keypoint_type person
```
Típusok: `person`, `animal`, `hand`

### 4. OCR - Box (`ocr_box`)
Szöveg detektálás téglalap formában.
```bash
python camera_detection.py --task ocr_box --categories text
```

### 5. OCR - Polygon (`ocr_polygon`)
Szöveg detektálás polygon formában (pontosabb).
```bash
python camera_detection.py --task ocr_polygon --categories text
```

---

## ⚙️ Teljesítmény Optimalizálás

### Lassú gép vagy régi laptop?
```bash
python camera_detection.py \
  --fps 1 \
  --categories person \
  --max_tokens 512
```
- Alacsony FPS (1-2)
- Kevés kategória (1-3)
- Kevesebb token

### Átlagos teljesítményű gép?
```bash
python camera_detection.py \
  --fps 5 \
  --categories person car dog cat
```
- Közepes FPS (3-6)
- Normál kategória szám (3-6)

### Erős gép GPU-val?
```bash
python camera_detection.py \
  --fps 10 \
  --categories person car dog cat phone laptop cup bottle
```
- Magas FPS (7-10+)
- Több kategória (5-10)

### Felbontás csökkentése
Ha még mindig lassú, módosítsd a szkriptben:
```python
# camera_detection.py vagy interactive_camera_demo.py
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 1280 helyett
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 720 helyett
```

---

## 🐛 Gyakori Problémák és Megoldások

### ❌ Kamera nem nyílik meg
**Probléma:** "Failed to open camera: 0"

**Megoldás:**
```bash
# Próbálj más indexet
python camera_detection.py --camera 1
python camera_detection.py --camera 2

# Vagy Linux-on ellenőrizd
ls /dev/video*
```

### ❌ Lassú feldolgozás
**Probléma:** Túl lassú az FPS

**Megoldás:**
1. Csökkentsd az FPS-t: `--fps 2`
2. Kevesebb kategória: `--categories person`
3. Csökkentsd a felbontást (lásd fent)
4. Használj GPU-t

### ❌ CUDA out of memory
**Probléma:** "CUDA out of memory" hiba

**Megoldás:**
```bash
# Kevesebb token
python camera_detection.py --max_tokens 512

# Vagy CPU mód
# (a transformers backend automatikusan CPU-ra vált ha nincs GPU)
```

### ❌ Modell nem található
**Probléma:** "Model path not found"

**Megoldás:**
```bash
# Ellenőrizd a modellt
ls -la models/Rex-Omni/

# Ha nincs, töltsd le
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni
```

### ❌ Import Error
**Probléma:** "ModuleNotFoundError: No module named 'cv2'"

**Megoldás:**
```bash
pip install opencv-python
# vagy
pip install -r requirements.txt
```

---

## 📊 Összehasonlító Táblázat

| Szkript | Nehézség | Interaktivitás | Teljesítmény | Használati Eset |
|---------|----------|----------------|--------------|-----------------|
| `simple_camera_demo.py` | ⭐ Könnyű | ❌ Nincs | 🟢 Gyors | Gyors teszt, egy kép |
| `camera_detection.py` | ⭐⭐ Közepes | ⚠️ Korlátozott | 🟢 Gyors | Egyedi beállítások |
| `interactive_camera_demo.py` | ⭐ Könnyű | ✅ Teljes | 🟢 Gyors | Demo, kísérletezés |

---

## 🎓 Kód Struktúra

```
rex-omni/
├── 📄 Python szkriptek
│   ├── simple_camera_demo.py      # Egyszerű demo
│   ├── camera_detection.py        # Valós idejű detektálás
│   └── interactive_camera_demo.py # Interaktív mód
│
├── 📚 Dokumentáció
│   ├── README_CAMERA.md           # Részletes útmutató (HU)
│   ├── QUICKSTART.md              # Gyors összefoglaló (HU)
│   └── THIS_FILE.md               # Ez a fájl
│
├── 🛠️ Segédeszközök
│   ├── check_system.py            # Rendszer ellenőrző
│   └── setup_camera.sh            # Telepítő script
│
├── 📦 Eredeti ComfyUI fájlok
│   ├── rex_omni_nodes.py          # ComfyUI node-ok
│   ├── utils.py                   # Segédfüggvények
│   └── src/rex_omni/              # Rex-Omni wrapper
│       ├── wrapper.py
│       ├── tasks.py
│       ├── parser.py
│       └── utils.py
│
└── 📋 Konfiguráció
    ├── requirements.txt           # Python függőségek
    ├── pyproject.toml
    └── README.md                  # Fő README (frissítve)
```

---

## 🌟 Jellemzők és Képességek

### ✅ Amit tud

1. **Real-time Object Detection**
   - Folyamatos detektálás webkameráról/IP kameráról
   - 1-10 FPS (beállítható)
   - Több kategória egyidejű keresése

2. **Többféle Feladat**
   - Object Detection (bounding box)
   - Object Pointing (középpont)
   - Keypoint Detection (póz)
   - OCR (szövegfelismerés)

3. **Interaktív Kontroll**
   - Futás közbeni kategória váltás
   - 7 előre beállított preset
   - Szünet/folytatás
   - Kép mentés

4. **Optimalizálás**
   - FPS kontroll
   - GPU/CPU automatikus választás
   - Memória optimalizálás

5. **Vizualizáció**
   - Real-time bounding box-ok
   - FPS kijelzés
   - Detektálások száma
   - Kategória információk

### ⚠️ Korlátok

1. **Teljesítmény**
   - Nagy felbontás lassabb
   - Sok kategória lassabb
   - CPU mód lassabb mint GPU

2. **Modell méret**
   - ~6 GB lemezterület
   - ~4-8 GB RAM futáshoz
   - GPU ajánlott (de nem kötelező)

3. **Kamera**
   - USB webkamera vagy IP kamera szükséges
   - Néhány IP kamera nem kompatibilis

---

## 📚 További Források

### Hivatalos Dokumentáció
- **Rex-Omni honlap:** https://rex-omni.github.io/
- **GitHub repo:** https://github.com/IDEA-Research/Rex-Omni
- **Hugging Face:** https://huggingface.co/IDEA-Research/Rex-Omni
- **Paper:** https://arxiv.org/abs/2510.12798

### Tutorialok
- **Hivatalos tutorial-ok:** https://github.com/IDEA-Research/Rex-Omni/tree/master/tutorials
- **Gradio demo:** https://huggingface.co/spaces/Mountchicken/Rex-Omni

### Egyéb
- **COCO dataset:** https://cocodataset.org/
- **OpenCV dokumentáció:** https://docs.opencv.org/

---

## ✅ Telepítési Ellenőrzőlista

Mielőtt elkezdenéd, győződj meg róla, hogy:

- [ ] Python 3.8+ telepítve van
- [ ] `pip` működik
- [ ] Elegendő lemezterület (min. 10 GB)
- [ ] Kamera elérhető
- [ ] Internet kapcsolat (modell letöltéséhez)

**Telepítés:**
- [ ] `pip install -r requirements.txt` lefutott
- [ ] `pip install opencv-python` lefutott
- [ ] Rex-Omni modell letöltve (`models/Rex-Omni/`)
- [ ] `python check_system.py` minden zöld ✓

**Első futtatás:**
- [ ] `python simple_camera_demo.py` működik
- [ ] Kamera képe látszik
- [ ] Detektálás működik

**Opcionális:**
- [ ] GPU működik (gyorsabb)
- [ ] Virtual environment létrehozva (tisztább)

---

## 🎉 Összefoglalás

### Mit kaptál?

1. **3 használatra kész Python szkript**
   - Egyszerű, haladó és interaktív mód
   - Minden dokumentálva és tesztelve

2. **Teljes magyar dokumentáció**
   - Részletes útmutatók
   - Példák és tutorialok
   - Hibaelhárítási segítség

3. **Segédeszközök**
   - Automatikus telepítő
   - Rendszer ellenőrző

4. **Támogatás minden szinten**
   - Kezdőknek: `simple_camera_demo.py`
   - Haladóknak: `camera_detection.py`
   - Mindenkinek: `interactive_camera_demo.py`

### Következő lépés?

```bash
# 1. Ellenőrizd a rendszert
python check_system.py

# 2. Ha minden OK, indulás!
python interactive_camera_demo.py
```

**Sok sikert! 🚀**

---

## 📞 Segítség

Ha elakadtál:

1. Olvasd el: `README_CAMERA.md`
2. Futtasd: `python check_system.py`
3. Nézd meg: `QUICKSTART.md`
4. Ellenőrizd a [GitHub Issues](https://github.com/IDEA-Research/Rex-Omni/issues)-t

---

**Készítette:** GitHub Copilot  
**Dátum:** 2026. január 13.  
**Verzió:** 1.0  
**Licenc:** MIT (az eredeti ComfyUI-RexOmni projekt alapján)
