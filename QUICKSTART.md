# Rex-Omni Kamerás Object Detection - Gyors Összefoglaló

## 📦 Amit készítettem

### 1. **simple_camera_demo.py** - Egyszerű Demo
- Egy képet készít a kameráddal
- Elemzi az objektumokat
- Megjeleníti és menti az eredményt
- **Kezdőknek ideális!**

### 2. **camera_detection.py** - Valós Idejű Detektálás
- Folyamatosan elemzi a kamera képét
- Beállítható FPS és kategóriák
- Mentési és szüneteltetési funkciók
- **Teljes kontroll a paraméterek felett**

### 3. **interactive_camera_demo.py** - Interaktív Mód
- Futás közben változtatható kategóriák (1-7 gombokkal)
- Vizuális információs panel
- 7 előre definiált kategória preset
- **Legkényelmesebb használat**

### 4. **README_CAMERA.md** - Magyar Dokumentáció
- Teljes telepítési útmutató
- Minden funkció részletes leírása
- Példák különböző használati esetekre
- Hibaelhárítási tanácsok

### 5. **setup_camera.sh** - Telepítő Script
- Automatikus függőség telepítés
- Opcionális virtual environment
- Modell letöltési segítség

## 🚀 Gyors Start (3 lépés)

```bash
# 1. Telepítés
./setup_camera.sh

# 2. Modell letöltése (ha még nem történt meg)
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni

# 3. Futtatás
python interactive_camera_demo.py
```

## 💡 Melyiket válasszam?

### Egyszerű próba (1 kép)?
```bash
python simple_camera_demo.py
```
- Gyors, könnyű
- Nem kell paraméter
- Jó első próbálkozásnak

### Valós idejű detektálás egyedi beállításokkal?
```bash
python camera_detection.py --categories person car dog --fps 3
```
- Teljes kontroll
- Parancssori argumentumok
- Saját kategóriák megadása

### Interaktív használat?
```bash
python interactive_camera_demo.py
```
- Futás közben váltható kategóriák
- 7 előre definiált preset
- Vizuális felület
- **AJÁNLOTT KEZDÉSNEK!**

## 📋 Előre Definiált Presets (Interaktív módban)

Az **interactive_camera_demo.py**-ban az alábbi preseteket választhatod:

1. **Emberek** - Csak emberek
2. **Járművek** - Autók, motorok, buszok, stb.
3. **Állatok** - Kutyák, macskák, lovak, stb.
4. **Elektronika** - Telefonok, laptopok, TV-k
5. **Bútorok** - Székek, ágyak, asztalok
6. **Konyha** - Poharak, evőeszközök, tálak
7. **Minden** - Mind a 80 COCO kategória

Futás közben nyomd meg az **1-7** számokat a váltáshoz!

## 🎯 Példa használati esetek

### Térfigyelés (emberek számlálása)
```bash
python camera_detection.py --categories person --fps 2
```

### Forgalomfigyelés
```bash
python camera_detection.py --categories car truck bus motorcycle bicycle --fps 3
```

### Póz detektálás (fitness, sport)
```bash
python camera_detection.py --task keypoint --keypoint_type person --fps 5
```

### OCR (dokumentum szkenner)
```bash
python camera_detection.py --task ocr_polygon --categories text --fps 2
```

### IP kamera
```bash
python camera_detection.py --camera "rtsp://192.168.1.100:554/stream" --fps 2
```

## ⚙️ Gyakori Paraméterek

| Paraméter | Leírás | Alapértelmezett |
|-----------|--------|-----------------|
| `--fps` | Feldolgozási sebesség | 5 |
| `--categories` | Keresendő objektumok | person car dog cat phone laptop |
| `--task` | Feladat típus | detection |
| `--backend` | Háttér (transformers/vllm) | transformers |
| `--camera` | Kamera forrás | 0 |

## 🎮 Billentyűparancsok

### Minden szkriptben:
- **Q** - Kilépés
- **S** - Kép mentése
- **P** - Szünet/folytatás

### Interactive módban (interactive_camera_demo.py):
- **1-7** - Kategória preset váltás
- **H** - Súgó panel be/ki

## 📊 Teljesítmény optimalizálás

### Lassú gép?
```bash
python camera_detection.py --fps 2 --categories person
```
- Kevesebb FPS
- Kevesebb kategória

### Gyors gép?
```bash
python camera_detection.py --fps 10 --categories person car dog cat phone laptop
```
- Több FPS
- Több kategória

### GPU problémák?
- Csökkentsd az `--max_tokens` értékét (pl. 512)
- Használj kisebb felbontást (módosítsd a kódban)

## 📚 További Információk

- **Részletes dokumentáció**: [README_CAMERA.md](README_CAMERA.md)
- **Hivatalos oldal**: https://rex-omni.github.io/
- **GitHub**: https://github.com/IDEA-Research/Rex-Omni
- **Hugging Face**: https://huggingface.co/IDEA-Research/Rex-Omni

## 🐛 Problémák?

### Kamera nem nyílik meg
```bash
# Próbáld ki más indexet
python camera_detection.py --camera 1  # vagy 2, 3...
```

### Lassú feldolgozás
```bash
# Csökkentsd az FPS-t
python camera_detection.py --fps 1
```

### CUDA out of memory
```bash
# Használj CPU-t vagy csökkentsd a tokeneket
python camera_detection.py --max_tokens 512
```

### Modell nem található
```bash
# Töltsd le újra
huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni

# Ellenőrizd
ls -la models/Rex-Omni/
```

## ✅ Ellenőrzőlista

- [ ] Python 3.8+ telepítve
- [ ] Függőségek telepítve (`pip install -r requirements.txt`)
- [ ] OpenCV telepítve (`pip install opencv-python`)
- [ ] Rex-Omni modell letöltve (`models/Rex-Omni/`)
- [ ] Kamera működik
- [ ] Szkript futtatható

## 🎉 Kész!

Most már készen állsz a Rex-Omni kamerás object detection használatára!

Kezdd az interaktív móddal:
```bash
python interactive_camera_demo.py
```

Sok sikert! 🚀
