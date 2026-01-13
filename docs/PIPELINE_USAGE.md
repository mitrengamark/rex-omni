# Factory Assembly Detection Pipeline

## 📋 Áttekintés

Batch objektum detektálási pipeline gyári összeszerelő állomásokhoz. A Rex-Omni modell használatával képes több képen egymás után elvégezni az objektum detektálást **40 általános kategória** felismerésével.

## 🎯 Felismerhető Objektumok

A pipeline a `COMMON_ASSEMBLY_OBJECTS` kategóriákat használja (40 db):

### Szerszámok (8 db)
- screwdriver, wrench, pliers, allen key, hammer
- tweezers, drill, soldering iron

### Alkatrészek
- **Rögzítők:** screw, bolt, nut, washer
- **Elektronika:** PCB, circuit board, wire, cable, sensor, motor, battery, connector, LED, resistor, capacitor
- **Mechanika:** gear, bearing, spring

### Mérőeszközök (4 db)
- caliper, multimeter, tape measure, ruler

### Segédeszközök
- **Anyagok:** tape, solder, glue
- **Tárolók:** box, tray, bin
- **Dokumentáció:** manual, label
- **Eszközök:** laptop, tablet

---

## 🚀 Gyors Kezdés

### 1. Pipeline Inicializálás

```python
from factory_assembly_pipeline import FactoryAssemblyPipeline

pipeline = FactoryAssemblyPipeline(
    model_path="IDEA-Research/Rex-Omni",  # vagy local path
    backend="transformers",                # vagy "vllm"
    output_dir="pipeline_results"
)
```

### 2. Egyetlen Kép Feldolgozása

```python
result = pipeline.process_single_image(
    image_path="factory_table.jpg",
    save_visualization=True,
    save_json=True
)

if result['success']:
    print(f"Talált: {result['total_count']} objektum")
    for obj_name, detections in result['found_objects'].items():
        print(f"  - {obj_name}: {len(detections)} db")
```

### 3. Batch Képek Feldolgozása

```python
image_paths = [
    "factory_table1.jpg",
    "factory_table2.jpg",
    "assembly_station.jpg"
]

results = pipeline.process_batch(
    image_paths=image_paths,
    save_visualization=True,
    save_json=True,
    print_summary=True
)
```

### 4. Könyvtár Feldolgozása

```python
results = pipeline.process_directory(
    directory="factory_images/",
    extensions=['.jpg', '.png'],
    save_visualization=True,
    save_json=True
)
```

---

## 📂 Kimenetek

A pipeline automatikusan elmenti az eredményeket:

### 1. Vizualizált Képek
```
{output_dir}/image_name_detected_YYYYMMDD_HHMMSS.jpg
```
- Bounding boxokkal jelölt objektumok
- Címkék az objektum nevével

### 2. JSON Eredmények
```json
{
  "image_path": "factory_table.jpg",
  "timestamp": "20260113_143052",
  "processing_time": 2.34,
  "categories_searched": ["screwdriver", "wrench", ...],
  "found_objects": {
    "screwdriver": [
      {"type": "box", "coords": [100, 200, 150, 300]},
      {"type": "box", "coords": [400, 150, 450, 250]}
    ],
    "PCB": [
      {"type": "box", "coords": [200, 100, 350, 200]}
    ]
  },
  "summary": {
    "total_object_types": 2,
    "total_objects": 3
  }
}
```

### 3. Batch Összefoglaló
```
{output_dir}/batch_summary_YYYYMMDD_HHMMSS.json
```
- Statisztikák az összes feldolgozott képről
- Sikeres/sikertelen feldolgozások
- Átlagos feldolgozási idő

---

## 💻 Parancssor Használat

### Példa Script Futtatása

```bash
python run_pipeline_examples.py
```

Választható opciók:
1. Egyetlen kép feldolgozása
2. Batch képek feldolgozása
3. Könyvtár feldolgozása
4. Mindhárom (demo)

---

## 🎓 Python API

### FactoryAssemblyPipeline Osztály

```python
class FactoryAssemblyPipeline:
    def __init__(
        self,
        model_path: str = "IDEA-Research/Rex-Omni",
        backend: str = "transformers",
        max_tokens: int = 512,
        temperature: float = 0.0,
        categories: Optional[List[str]] = None,
        output_dir: str = "pipeline_results"
    )
```

**Paraméterek:**
- `model_path`: Model elérési útvonal (HF repo vagy local)
- `backend`: "transformers" (lassabb, egyszerűbb) vagy "vllm" (gyorsabb)
- `max_tokens`: Max generált tokenek száma
- `temperature`: 0.0 = determinisztikus
- `categories`: Kategóriák listája (default: COMMON_ASSEMBLY_OBJECTS)
- `output_dir`: Kimeneti könyvtár

### Metódusok

#### process_single_image()
```python
result = pipeline.process_single_image(
    image_path: str,
    save_visualization: bool = True,
    save_json: bool = True
) -> Dict
```

**Returns:**
```python
{
    'success': True,
    'image_path': 'factory_table.jpg',
    'processing_time': 2.34,
    'found_objects': {'screwdriver': [...], 'PCB': [...]},
    'total_count': 5,
    'visualization_path': 'results/..._detected.jpg',
    'json_path': 'results/..._results.json'
}
```

#### process_batch()
```python
results = pipeline.process_batch(
    image_paths: List[str],
    save_visualization: bool = True,
    save_json: bool = True,
    print_summary: bool = True
) -> List[Dict]
```

#### process_directory()
```python
results = pipeline.process_directory(
    directory: str,
    extensions: List[str] = ['.jpg', '.jpeg', '.png'],
    **kwargs
) -> List[Dict]
```

---

## 📊 Statisztikák

A pipeline automatikusan gyűjti a statisztikákat:

```python
pipeline.stats = {
    'total_images': 10,
    'successful': 9,
    'failed': 1,
    'total_objects_detected': 47,
    'processing_times': [2.1, 2.3, 1.9, ...]
}
```

---

## 🔧 Konfigurációs Példák

### Gyors Feldolgozás (vLLM)
```python
pipeline = FactoryAssemblyPipeline(
    model_path="IDEA-Research/Rex-Omni",
    backend="vllm",
    max_tokens=256,  # Csökkentett
    output_dir="fast_results"
)
```

### Saját Kategóriák
```python
custom_categories = [
    "screwdriver", "wrench", "PCB", 
    "screw", "wire", "laptop"
]

pipeline = FactoryAssemblyPipeline(
    model_path="IDEA-Research/Rex-Omni",
    categories=custom_categories,
    output_dir="custom_results"
)
```

### Csak JSON, Nincs Vizualizáció
```python
results = pipeline.process_batch(
    image_paths=images,
    save_visualization=False,
    save_json=True
)
```

---

## 🐛 Hibaelhárítás

### Model Betöltési Hiba
```python
# Ha local model használsz:
pipeline = FactoryAssemblyPipeline(
    model_path="/path/to/local/Rex-Omni"
)

# Ha HuggingFace-ről töltöd:
pipeline = FactoryAssemblyPipeline(
    model_path="IDEA-Research/Rex-Omni"
)
```

### Memória Probléma (8GB RAM)
```python
pipeline = FactoryAssemblyPipeline(
    max_tokens=256,  # Csökkentve 512-ről
    backend="transformers"
)
```

### Lassú Feldolgozás
```python
# Használj vLLM-et
pipeline = FactoryAssemblyPipeline(
    backend="vllm"  # 2-3x gyorsabb
)
```

---

## 📁 Fájlstruktúra

```
rex-omni/
├── factory_assembly_categories.py   # Kategória definíciók
├── factory_assembly_pipeline.py     # Pipeline osztály
├── run_pipeline_examples.py         # Példa scriptek
├── factory_images/                  # Input képek könyvtára
└── pipeline_results/                # Output könyvtár
    ├── image1_detected_*.jpg
    ├── image1_results_*.json
    ├── image2_detected_*.jpg
    ├── image2_results_*.json
    └── batch_summary_*.json
```

---

## 🎯 Használati Esetek

### 1. Szerszámkészlet Ellenőrzés
```python
# Ellenőrizzük, milyen szerszámok vannak az asztalon
result = pipeline.process_single_image("toolbox.jpg")
tools = result['found_objects']
print(f"Talált szerszámok: {', '.join(tools.keys())}")
```

### 2. Összeszerelési Folyamat Dokumentáció
```python
# Több lépés dokumentálása
assembly_steps = [
    "step1_components.jpg",
    "step2_assembly.jpg",
    "step3_final.jpg"
]
results = pipeline.process_batch(assembly_steps)
```

### 3. Raktár Leltár
```python
# Összes kép feldolgozása a raktár mappából
results = pipeline.process_directory("warehouse_photos/")
```

### 4. Humanoid Robot Látórendszer
```python
# Robot látja az asztalt
from PIL import Image

robot_camera_image = Image.open("camera_feed.jpg")
result = pipeline.process_single_image("camera_feed.jpg")

# Robot válasza
found = result['found_objects']
robot_says = f"Az asztalon látok: {', '.join(found.keys())}"
```

---

## ⚙️ Optimalizációs Tippek

1. **Batch méret**: 2-5 kép egyszerre optimális (8GB RAM-mal)
2. **Backend**: vLLM 2-3x gyorsabb, de több memóriát használ
3. **max_tokens**: Csökkentsd ha gyorsabb feldolgozást akarsz
4. **Kategóriák**: Kevesebb kategória = gyorsabb detektálás

---

## 📚 További Információk

- Rex-Omni dokumentáció: [REX_OMNI_OBJECT_DETECTION_GUIDE.md](REX_OMNI_OBJECT_DETECTION_GUIDE.md)
- Kategória lista: [factory_assembly_categories.py](factory_assembly_categories.py)
- GitHub: https://github.com/IDEA-Research/Rex-Omni
- HuggingFace: https://huggingface.co/IDEA-Research/Rex-Omni
