#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Factory Assembly Detection Pipeline
Gyári Összeszerelő Állomás - Batch Objektum Detektálás Pipeline

Több képen egymás után elvégzi az objektum detektálást.
Felhasznált kategóriák: COMMON_ASSEMBLY_OBJECTS (40 db általános kategória)
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from PIL import Image

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to import from local ComfyUI-RexOmni repo first, then Rex-Omni repo
try:
    comfyui_src = os.path.join(current_dir, 'ComfyUI-RexOmni_repo', 'src')
    sys.path.insert(0, comfyui_src)
    from rex_omni.wrapper import RexOmniWrapper
    from rex_omni.utils import RexOmniVisualize
except ImportError:
    # Try Rex-Omni repo
    rex_omni_path = os.path.join(current_dir, 'Rex-Omni_repo')
    sys.path.insert(0, rex_omni_path)
    from rex_omni.wrapper import RexOmniWrapper
    from rex_omni.utils import RexOmniVisualize

from factory_assembly_categories import COMMON_ASSEMBLY_OBJECTS


class FactoryAssemblyPipeline:
    """
    Pipeline osztály gyári összeszerelő állomások batch objektum detektálásához
    """
    
    def __init__(
        self,
        model_path: str = "models/Rex-Omni",
        backend: str = "transformers",
        max_tokens: int = 512,
        temperature: float = 0.0,
        categories: Optional[List[str]] = None,
        output_dir: str = "pipeline_results"
    ):
        """
        Pipeline inicializálása
        
        Args:
            model_path: Rex-Omni modell elérési útja
            backend: "transformers" vagy "vllm"
            max_tokens: Maximum tokenek száma
            temperature: Sampling temperature
            categories: Kategóriák listája (None esetén COMMON_ASSEMBLY_OBJECTS)
            output_dir: Kimeneti könyvtár
        """
        self.model_path = model_path
        self.backend = backend
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.categories = categories or COMMON_ASSEMBLY_OBJECTS
        self.output_dir = output_dir
        
        # Output könyvtár létrehozása
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Model betöltése
        self.model = None
        self._load_model()
        
        # Statisztikák
        self.stats = {
            'total_images': 0,
            'successful': 0,
            'failed': 0,
            'total_objects_detected': 0,
            'processing_times': [],
        }
    
    def _load_model(self):
        """Model betöltése"""
        print("\n" + "="*70)
        print("FACTORY ASSEMBLY DETECTION PIPELINE")
        print("="*70 + "\n")
        
        print(f"⏳ Model betöltése: {self.model_path}")
        print(f"   Backend: {self.backend}")
        print(f"   Kategóriák: {len(self.categories)} db\n")
        
        try:
            self.model = RexOmniWrapper(
                model_path=self.model_path,
                backend=self.backend,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                attn_implementation="eager",  # macOS kompatibilitás
                device_map=None,  # macOS kompatibilitás
            )
            print("✓ Model sikeresen betöltve!\n")
        except Exception as e:
            print(f"❌ Model betöltési hiba: {e}\n")
            raise
    
    def process_single_image(
        self,
        image_path: str,
        save_visualization: bool = True,
        save_json: bool = True
    ) -> Dict:
        """
        Egyetlen kép feldolgozása
        
        Args:
            image_path: Kép elérési útja
            save_visualization: Vizualizáció mentése
            save_json: JSON eredmények mentése
        
        Returns:
            dict: Feldolgozási eredmények
        """
        start_time = time.time()
        
        # Kép betöltése
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {
                'success': False,
                'error': f"Kép betöltési hiba: {e}",
                'image_path': image_path
            }
        
        # Detektálás
        try:
            results = self.model.inference(
                images=image,
                task="detection",
                categories=self.categories
            )
            result = results[0]
        except Exception as e:
            return {
                'success': False,
                'error': f"Detektálási hiba: {e}",
                'image_path': image_path
            }
        
        processing_time = time.time() - start_time
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Ismeretlen hiba'),
                'image_path': image_path,
                'processing_time': processing_time
            }
        
        # Eredmények feldolgozása
        detected_objects = result['extracted_predictions']
        found_objects = {name: dets for name, dets in detected_objects.items() if dets}
        total_count = sum(len(dets) for dets in found_objects.values())
        
        # Fájlnév generálása
        image_name = Path(image_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Vizualizáció mentése
        vis_path = None
        if save_visualization and found_objects:
            try:
                vis_image = RexOmniVisualize(
                    image=image,
                    predictions=detected_objects,
                    font_size=15,
                    draw_width=3,
                    show_labels=True
                )
                vis_path = os.path.join(
                    self.output_dir,
                    f"{image_name}_detected_{timestamp}.jpg"
                )
                vis_image.save(vis_path)
            except Exception as e:
                print(f"⚠️  Vizualizáció mentési hiba: {e}")
        
        # JSON mentése
        json_path = None
        if save_json:
            try:
                json_data = {
                    'image_path': image_path,
                    'timestamp': timestamp,
                    'processing_time': processing_time,
                    'categories_searched': self.categories,
                    'found_objects': {
                        name: [
                            {
                                'type': det['type'],
                                'coords': det['coords']
                            } for det in dets
                        ] for name, dets in found_objects.items()
                    },
                    'summary': {
                        'total_object_types': len(found_objects),
                        'total_objects': total_count
                    }
                }
                json_path = os.path.join(
                    self.output_dir,
                    f"{image_name}_results_{timestamp}.json"
                )
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️  JSON mentési hiba: {e}")
        
        return {
            'success': True,
            'image_path': image_path,
            'processing_time': processing_time,
            'found_objects': found_objects,
            'total_count': total_count,
            'visualization_path': vis_path,
            'json_path': json_path
        }
    
    def process_batch(
        self,
        image_paths: List[str],
        save_visualization: bool = True,
        save_json: bool = True,
        print_summary: bool = True
    ) -> List[Dict]:
        """
        Batch képek feldolgozása
        
        Args:
            image_paths: Képek listája
            save_visualization: Vizualizációk mentése
            save_json: JSON eredmények mentése
            print_summary: Összefoglaló kiírása
        
        Returns:
            list: Feldolgozási eredmények listája
        """
        print("="*70)
        print(f"BATCH FELDOLGOZÁS - {len(image_paths)} kép")
        print("="*70 + "\n")
        
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"[{i}/{len(image_paths)}] Feldolgozás: {Path(image_path).name}")
            
            result = self.process_single_image(
                image_path=image_path,
                save_visualization=save_visualization,
                save_json=save_json
            )
            
            results.append(result)
            
            # Statisztikák frissítése
            self.stats['total_images'] += 1
            if result['success']:
                self.stats['successful'] += 1
                self.stats['total_objects_detected'] += result.get('total_count', 0)
                self.stats['processing_times'].append(result['processing_time'])
                
                # Eredmények kiírása
                found = result['found_objects']
                print(f"   ✓ Talált: {result['total_count']} objektum, {len(found)} típus")
                print(f"   ⏱  Idő: {result['processing_time']:.2f}s")
                if found:
                    top3 = sorted(found.items(), key=lambda x: len(x[1]), reverse=True)[:3]
                    print(f"   📦 Top: {', '.join([f'{len(v)} {k}' for k, v in top3])}")
            else:
                self.stats['failed'] += 1
                print(f"   ❌ Hiba: {result.get('error', 'Ismeretlen')}")
            
            print()
        
        if print_summary:
            self._print_summary()
        
        # Batch összefoglaló JSON
        self._save_batch_summary(results)
        
        return results
    
    def process_directory(
        self,
        directory: str,
        extensions: List[str] = ['.jpg', '.jpeg', '.png', '.bmp'],
        **kwargs
    ) -> List[Dict]:
        """
        Könyvtárban lévő összes kép feldolgozása
        
        Args:
            directory: Könyvtár elérési útja
            extensions: Képformátumok listája
            **kwargs: További paraméterek a process_batch-hez
        
        Returns:
            list: Feldolgozási eredmények
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"❌ Könyvtár nem létezik: {directory}")
            return []
        
        # Képek összegyűjtése
        image_paths = []
        for ext in extensions:
            image_paths.extend(dir_path.glob(f"*{ext}"))
            image_paths.extend(dir_path.glob(f"*{ext.upper()}"))
        
        image_paths = [str(p) for p in image_paths]
        
        if not image_paths:
            print(f"⚠️  Nem található kép a könyvtárban: {directory}")
            return []
        
        print(f"📁 Könyvtár: {directory}")
        print(f"   Talált képek: {len(image_paths)}\n")
        
        return self.process_batch(image_paths, **kwargs)
    
    def _print_summary(self):
        """Összefoglaló statisztikák kiírása"""
        print("\n" + "="*70)
        print("FELDOLGOZÁSI ÖSSZEFOGLALÓ")
        print("="*70 + "\n")
        
        print(f"  📊 Összesen feldolgozva: {self.stats['total_images']} kép")
        print(f"  ✓ Sikeres: {self.stats['successful']}")
        print(f"  ❌ Sikertelen: {self.stats['failed']}")
        print(f"  📦 Összes detektált objektum: {self.stats['total_objects_detected']}")
        
        if self.stats['processing_times']:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            min_time = min(self.stats['processing_times'])
            max_time = max(self.stats['processing_times'])
            print(f"\n  ⏱  Feldolgozási idő:")
            print(f"     Átlag: {avg_time:.2f}s")
            print(f"     Min: {min_time:.2f}s")
            print(f"     Max: {max_time:.2f}s")
        
        print(f"\n  💾 Eredmények: {self.output_dir}/")
        print("="*70 + "\n")
    
    def _save_batch_summary(self, results: List[Dict]):
        """Batch összefoglaló JSON mentése"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = os.path.join(
            self.output_dir,
            f"batch_summary_{timestamp}.json"
        )
        
        summary = {
            'timestamp': timestamp,
            'total_images': self.stats['total_images'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'total_objects_detected': self.stats['total_objects_detected'],
            'categories_used': self.categories,
            'results': [
                {
                    'image': r['image_path'],
                    'success': r['success'],
                    'objects_found': len(r.get('found_objects', {})),
                    'total_count': r.get('total_count', 0),
                    'processing_time': r.get('processing_time', 0)
                } for r in results
            ]
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Batch összefoglaló: {summary_path}\n")


def main():
    """Példa használat"""
    
    print("\n" + "="*70)
    print("FACTORY ASSEMBLY DETECTION PIPELINE - PÉLDA")
    print("="*70 + "\n")
    
    # Pipeline inicializálása
    pipeline = FactoryAssemblyPipeline(
        model_path="IDEA-Research/Rex-Omni",  # vagy local: "models/Rex-Omni"
        backend="transformers",
        max_tokens=512,
        temperature=0.0,
        categories=COMMON_ASSEMBLY_OBJECTS,  # 40 db általános kategória
        output_dir="pipeline_results"
    )
    
    print("\nHASZNÁLATI MÓDOK:")
    print("-"*70)
    print("""
1. EGYETLEN KÉP FELDOLGOZÁSA:
   
   result = pipeline.process_single_image("image.jpg")
   print(result['found_objects'])

2. TÖBB KÉP BATCH FELDOLGOZÁSA:
   
   image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
   results = pipeline.process_batch(image_paths)

3. KÖNYVTÁR FELDOLGOZÁSA:
   
   results = pipeline.process_directory("images/")

4. PYTHON KÓDBÓL:
   
   from factory_assembly_pipeline import FactoryAssemblyPipeline
   
   pipeline = FactoryAssemblyPipeline(
       model_path="models/Rex-Omni",
       output_dir="my_results"
   )
   
   # Képek feldolgozása
   results = pipeline.process_batch([
       "factory_table1.jpg",
       "factory_table2.jpg",
       "assembly_station.jpg"
   ])
   
   # Eredmények elemzése
   for result in results:
       if result['success']:
           print(f"{result['image_path']}:")
           for obj, dets in result['found_objects'].items():
               print(f"  - {obj}: {len(dets)} db")
    """)
    
    print("\nKIMENETEK:")
    print("-"*70)
    print("""
• Vizualizált képek: {output_dir}/*_detected_*.jpg
• JSON eredmények: {output_dir}/*_results_*.json
• Batch összefoglaló: {output_dir}/batch_summary_*.json
    """)
    
    print("\nKATEGÓRIÁK ({} db):".format(len(COMMON_ASSEMBLY_OBJECTS)))
    print("-"*70)
    for i, cat in enumerate(COMMON_ASSEMBLY_OBJECTS, 1):
        if i % 5 == 0:
            print(f"{cat},")
        else:
            print(f"{cat}, ", end="")
    print("\n")


if __name__ == "__main__":
    main()
