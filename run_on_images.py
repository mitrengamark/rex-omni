#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run Pipeline on Images Folder
Futtatja a factory assembly pipeline-t az images mappán
"""

import os
import sys

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

from factory_assembly_pipeline import FactoryAssemblyPipeline


def main():
    print("\n" + "="*70)
    print("FACTORY ASSEMBLY PIPELINE - IMAGES MAPPA FELDOLGOZÁSA")
    print("="*70 + "\n")
    
    # Ellenőrizzük hogy létezik-e az images mappa
    images_dir = "images"
    
    if not os.path.exists(images_dir):
        print(f"❌ Az '{images_dir}' mappa nem létezik!")
        print(f"   Hozd létre és helyezz bele képeket.")
        return
    
    # Pipeline inicializálása
    print("🚀 Pipeline inicializálása...\n")
    print("ℹ️  macOS mód: eager attention használata\n")
    
    pipeline = FactoryAssemblyPipeline(
        model_path="IDEA-Research/Rex-Omni",
        backend="transformers",
        max_tokens=512,
        temperature=0.0,
        output_dir="pipeline_results"
    )
    
    # Könyvtár feldolgozása
    print(f"📁 Feldolgozás: {images_dir}/\n")
    
    results = pipeline.process_directory(
        directory=images_dir,
        extensions=['.jpg', '.jpeg', '.png', '.bmp'],
        save_visualization=True,
        save_json=True,
        print_summary=True
    )
    
    # További részletek
    print("\n" + "="*70)
    print("RÉSZLETES EREDMÉNYEK")
    print("="*70 + "\n")
    
    for i, result in enumerate(results, 1):
        img_name = os.path.basename(result['image_path'])
        
        if result['success']:
            print(f"{i:2}. {img_name}")
            print(f"    ✓ {result['total_count']} objektum, {len(result['found_objects'])} típus")
            
            # Top 5 objektum
            if result['found_objects']:
                top5 = sorted(
                    result['found_objects'].items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:5]
                for obj_name, dets in top5:
                    print(f"       • {obj_name}: {len(dets)} db")
        else:
            print(f"{i:2}. {img_name}")
            print(f"    ❌ {result.get('error', 'Ismeretlen hiba')}")
        print()
    
    print("="*70)
    print(f"✅ KÉSZ! Eredmények: pipeline_results/")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
