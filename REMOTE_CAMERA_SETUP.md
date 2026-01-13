# Távoli Kamera Használat (Remote Camera Setup)

## Probléma
A szerver gépen nincs kamera, de a laptopról szeretnénk streamelni.

## Megoldás

### 1. LAPTOPON (ahol van kamera)

Telepítsd a Flask-ot:
```bash
pip install flask opencv-python
```

Indítsd el a kamera szervert:
```bash
python camera_server.py
```

Ez elindít egy HTTP szervert a `5000`-es porton. Látni fogod az IP címet, pl:
```
Server IP: 192.168.1.100
Stream URL: http://192.168.1.100:5000/video
```

**Teszteld böngészőből:**
Nyisd meg: `http://localhost:5000/test`

Ha látod a kamerát, működik! ✓

### 2. SZERVEREN (ahol a detektálás fut)

Használd a stream URL-t:
```bash
python live_video_detection.py --stream http://192.168.1.100:5000/video
```

**Helyettesítsd** a `192.168.1.100`-at a laptop tényleges IP címével!

## Teljes Munkafolyamat

```
┌─────────────────┐                    ┌──────────────────┐
│   LAPTOP        │   HTTP Stream      │    SZERVER       │
│  (kamera)       │ ─────────────────> │  (detektálás)    │
│                 │                    │                  │
│ camera_server.py│                    │ live_video_      │
│ :5000           │                    │ detection.py     │
└─────────────────┘                    └──────────────────┘
```

## Vezérlés

A szerveren:
- **SPACE** - Snapshot készítése és detektálás
- **Q** - Kilépés

## Hibaelhárítás

### "Connection refused"
- Ellenőrizd hogy a camera_server fut-e a laptopon
- Ellenőrizd a tűzfal beállításokat (5000-es port)
- Próbáld ping-elni a laptopot a szerverről

### "Can't open camera by index"
- Ez normális a szerveren - használd a --stream opciót!

### Lassú stream
- Csökkentsd a felbontást a camera_server.py-ban (640x480)
- Ellenőrizd a hálózati kapcsolatot

## Példák

### Laptop kamera stream (alapértelmezett kamera)
```bash
# Laptop:
python camera_server.py

# Szerver:
python live_video_detection.py --stream http://LAPTOP_IP:5000/video
```

### Külső USB kamera
```bash
# Laptop (kamera ID = 1):
python camera_server.py --camera 1

# Szerver:
python live_video_detection.py --stream http://LAPTOP_IP:5000/video
```

### Másik port használata
```bash
# Laptop (8080-as port):
python camera_server.py --port 8080

# Szerver:
python live_video_detection.py --stream http://LAPTOP_IP:8080/video
```

## Hálózati követelmények

- Laptop és szerver ugyanazon a hálózaton (LAN)
- Vagy SSH port forward:
  ```bash
  ssh -L 5000:localhost:5000 user@laptop
  # Ekkor: --stream http://localhost:5000/video
  ```

## Teljesítmény

- **Helyi hálózat (LAN)**: ~30 FPS, minimális késleltetés
- **WiFi**: ~15-20 FPS, enyhe késleltetés  
- **SSH tunnel**: ~10-15 FPS, nagyobb késleltetés

---

💡 **Tipp**: Ha gyakran használod, készíts alias-t:
```bash
# ~/.bashrc vagy ~/.zshrc
alias start-camera="python ~/rex-omni/camera_server.py"
alias detect-stream="python ~/rex-omni/live_video_detection.py --stream http://192.168.1.100:5000/video"
```
