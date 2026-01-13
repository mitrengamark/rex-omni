#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gyári Összeszerelő Állomás - Objektum Kategóriák
Factory Assembly Station - Object Categories for Rex-Omni Detection

A humanoid robot számára, amely le tudja írni az asztalon lévő tárgyakat.
"""

# ============================================================================
# ALKATRÉSZEK (COMPONENTS)
# ============================================================================

FASTENERS = [
    # Csavarok és anyák - általános
    "screw",
    "bolt", 
    "nut",
    "washer",
]

ELECTRONIC_COMPONENTS = [
    # Alapvető alkatrészek - általános
    "PCB",
    "circuit board",
    "microcontroller",
    
    # Kábelek és csatlakozók
    "wire",
    "cable",
    "connector",
    
    # Szenzorok és motorok
    "sensor",
    "motor",
    
    # Passzív alkatrészek
    "resistor",
    "capacitor",
    "LED",
    "transistor",
    "battery",
    "power supply",
]

MECHANICAL_PARTS = [
    # Mechanikai alkatrészek
    "gear",
    "bearing",
    "pulley",
    "belt",
    "shaft",
    "bracket",
    "mounting plate",
    "aluminum profile",
    "metal beam",
    "spring",
    
    # Csatlakozók
    "joint",
    "coupling",
    "clamp",
    "hinge",
]

# ============================================================================
# SZERSZÁMOK (TOOLS)
# ============================================================================

HAND_TOOLS = [
    # Alapszerszámok - általános
    "screwdriver",
    "wrench",
    "pliers",
    "hammer",
    "allen key",
    "tweezers",
]

POWER_TOOLS = [
    "drill",
    "soldering iron",
    "heat gun",
    "glue gun",
]

MEASURING_TOOLS = [
    "caliper",
    "micrometer",
    "tape measure",
    "ruler",
    "multimeter",
]

# ============================================================================
# ANYAGOK ÉS SEGÉDESZKÖZÖK (MATERIALS & SUPPLIES)
# ============================================================================

MATERIALS = [
    # Ragasztók és szerelési anyagok
    "glue",
    "tape",
    "solder",
    
    # Tisztítás
    "cloth",
    "brush",
]

CONTAINERS_AND_STORAGE = [
    # Tárolók - általános
    "box",
    "tray",
    "bin",
    "drawer",
]

# ============================================================================
# DOKUMENTÁCIÓ ÉS ESZKÖZÖK (DOCUMENTATION & DEVICES)
# ============================================================================

DOCUMENTATION = [
    "manual",
    "blueprint",
    "label",
]

DEVICES = [
    "laptop",
    "tablet",
    "monitor",
    "keyboard",
    "mouse",
    "webcam",
    "phone",
]

# ============================================================================
# BIZTONSÁG ÉS VÉDELEM (SAFETY)
# ============================================================================

SAFETY_EQUIPMENT = [
    "safety glasses",
    "gloves",
    "mask",
]

# ============================================================================
# KOMPLETT LISTÁK
# ============================================================================

# Minden kategória összevonva
ALL_FACTORY_OBJECTS = (
    FASTENERS +
    ELECTRONIC_COMPONENTS +
    MECHANICAL_PARTS +
    HAND_TOOLS +
    POWER_TOOLS +
    MEASURING_TOOLS +
    MATERIALS +
    CONTAINERS_AND_STORAGE +
    DOCUMENTATION +
    DEVICES +
    SAFETY_EQUIPMENT
)

# Általános objektumok (gyári összeszerelő állomáshoz)
COMMON_ASSEMBLY_OBJECTS = [
    # Szerszámok
    "screwdriver", "wrench", "pliers", "allen key", "hammer",
    "tweezers", "drill", "soldering iron",
    
    # Csavarok és rögzítők
    "screw", "bolt", "nut", "washer",
    
    # Elektronikai alkatrészek
    "PCB", "circuit board", "wire", "cable",
    "sensor", "motor", "battery", "connector",
    "LED", "resistor", "capacitor",
    
    # Mechanikai alkatrészek
    "gear", "bearing", "spring",
    
    # Mérőeszközök
    "caliper", "multimeter", "tape measure", "ruler",
    
    # Anyagok
    "tape", "solder", "glue",
    
    # Tárolók
    "box", "tray", "bin",
    
    # Dokumentáció
    "manual", "label",
    
    # Eszközök
    "laptop", "tablet",
    
    # Átmeneti kategóriák - általános objektumok
    "face", "person", "human", "man", "woman", "hand",
    "book", "books", 
    "air conditioner", "AC unit", "clima", "air conditioning",
    "phone", "mobile phone", "smartphone", "iPhone", "cell phone",
    "curtain", "pink curtain", "wall", "ceiling",
    "keyboard", "mouse", "monitor", "screen", "display",
    "cup", "mug", "bottle", "glass",
    "pen", "pencil", "paper", "notebook", "document",
    "chair", "desk", "table", "furniture",
    "plant", "flower", "headphones", "glasses", "eyeglasses",
    "watch", "clock", "backpack", "bag", "purse",
    "charger", "cable", "remote control", "controller",
    "shirt", "clothing", "sweater", "jacket",
]

# Leíró változatok kikapcsolva - csak általános kategóriák
DESCRIPTIVE_CATEGORIES = []


# ============================================================================
# PÉLDA HASZNÁLAT
# ============================================================================

def get_categories_for_robot(level="common"):
    """
    Kategóriák lekérése a robot látási rendszeréhez
    
    Args:
        level: "common" (gyakori), "all" (összes), "detailed" (leíró is)
    
    Returns:
        List of category strings
    """
    if level == "common":
        return COMMON_ASSEMBLY_OBJECTS
    elif level == "all":
        return list(set(ALL_FACTORY_OBJECTS))  # Deduplikálva
    elif level == "detailed":
        return list(set(COMMON_ASSEMBLY_OBJECTS + DESCRIPTIVE_CATEGORIES))
    else:
        return COMMON_ASSEMBLY_OBJECTS


def print_category_summary():
    """Összefoglaló statisztika"""
    print("\n" + "="*70)
    print("GYÁRI ÖSSZESZERELŐ ÁLLOMÁS - OBJEKTUM KATEGÓRIÁK")
    print("="*70 + "\n")
    
    categories = {
        "Csavarok, anyák (Fasteners)": len(FASTENERS),
        "Elektronikai alkatrészek": len(ELECTRONIC_COMPONENTS),
        "Mechanikai alkatrészek": len(MECHANICAL_PARTS),
        "Kézi szerszámok": len(HAND_TOOLS),
        "Elektromos szerszámok": len(POWER_TOOLS),
        "Mérőeszközök": len(MEASURING_TOOLS),
        "Anyagok és ragasztók": len(MATERIALS),
        "Tárolók és dobozok": len(CONTAINERS_AND_STORAGE),
        "Dokumentáció": len(DOCUMENTATION),
        "Eszközök (laptop, tablet)": len(DEVICES),
        "Védőfelszerelés": len(SAFETY_EQUIPMENT),
    }
    
    total = 0
    for name, count in categories.items():
        print(f"  • {name:.<50} {count:>3} db")
        total += count
    
    print("\n" + "-"*70)
    print(f"  ÖSSZES KATEGÓRIA: {total} db")
    print(f"  GYAKORI (optimalizált): {len(COMMON_ASSEMBLY_OBJECTS)} db")
    print(f"  LEÍRÓ VÁLTOZATOK: {len(DESCRIPTIVE_CATEGORIES)} db")
    print("="*70 + "\n")


if __name__ == "__main__":
    print_category_summary()
    
    print("\nGYAKORI OBJEKTUMOK LISTÁJA:")
    print("-" * 70)
    for i, obj in enumerate(COMMON_ASSEMBLY_OBJECTS, 1):
        print(f"{i:3}. {obj}")
    
    print("\n\nPÉLDA HASZNÁLAT:")
    print("-" * 70)
    print("""
from factory_assembly_categories import get_categories_for_robot
from rex_omni import RexOmniWrapper, RexOmniVisualize
from PIL import Image

# Robot látórendszer inicializálása
model = RexOmniWrapper(model_path="models/Rex-Omni", backend="transformers")

# Kategóriák betöltése
categories = get_categories_for_robot(level="common")  # 50+ kategória
# vagy: level="all" (100+ kategória)
# vagy: level="detailed" (leíró változatokkal)

# Kép feldolgozása
image = Image.open("assembly_table.jpg").convert("RGB")
results = model.inference(images=image, task="detection", categories=categories)

# Eredmények
result = results[0]
if result['success']:
    detected_objects = result['extracted_predictions']
    
    print("\\nAZ ASZTALON TALÁLHATÓ TÁRGYAK:")
    print("="*50)
    for obj_name, detections in detected_objects.items():
        if detections:  # Ha talált ilyen objektumot
            print(f"  • {obj_name}: {len(detections)} darab")
    
    # Robot válasza természetes nyelven
    obj_list = [f"{len(dets)} {name}" for name, dets in detected_objects.items() if dets]
    robot_response = f"Az asztalon {len(obj_list)} különböző típusú tárgy van: {', '.join(obj_list)}."
    print(f"\\nROBOT VÁLASZA:\\n{robot_response}")
    """)
