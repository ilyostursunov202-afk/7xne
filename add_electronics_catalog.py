#!/usr/bin/env python3
"""
Script to add comprehensive electronics catalog with categories and products
"""

import os
import sys
import asyncio
from datetime import datetime, timezone
import uuid
from pymongo import MongoClient
import requests
import json

# Add backend to path
sys.path.append('/app/backend')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/marketplace_db')
client = MongoClient(MONGO_URL)
db = client.marketplace_db
products_collection = db['products']

# Electronics categories and products
ELECTRONICS_CATALOG = {
    "smartphones": {
        "name": "Smartphones",
        "description": "Latest smartphones and mobile devices",
        "products": [
            {
                "name": "iPhone 15 Pro Max",
                "brand": "Apple",
                "price": 1199.99,
                "original_price": 1299.99,
                "description": "Latest iPhone with A17 Pro chip, titanium design, and advanced camera system",
                "features": ["A17 Pro chip", "48MP main camera", "Titanium design", "USB-C", "5G"],
                "specs": {
                    "display": "6.7-inch Super Retina XDR",
                    "storage": "256GB",
                    "camera": "48MP Pro camera system",
                    "battery": "Up to 29 hours video playback",
                    "os": "iOS 17"
                }
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "brand": "Samsung",
                "price": 1099.99,
                "description": "Premium Android flagship with S Pen and AI features",
                "features": ["200MP camera", "S Pen included", "AI photography", "120Hz display", "5G"],
                "specs": {
                    "display": "6.8-inch Dynamic AMOLED 2X",
                    "storage": "256GB", 
                    "camera": "200MP main camera",
                    "battery": "5000mAh",
                    "os": "Android 14"
                }
            },
            {
                "name": "Google Pixel 8 Pro",
                "brand": "Google",
                "price": 899.99,
                "description": "Google's flagship phone with pure Android and AI photography",
                "features": ["Tensor G3 chip", "AI photography", "Pure Android", "Magic Eraser", "5G"],
                "specs": {
                    "display": "6.7-inch LTPO OLED",
                    "storage": "128GB",
                    "camera": "50MP main camera",
                    "battery": "5050mAh",
                    "os": "Android 14"
                }
            }
        ]
    },
    
    "laptops": {
        "name": "Laptops & Computers",
        "description": "High-performance laptops and desktop computers",
        "products": [
            {
                "name": "MacBook Pro 16-inch M3 Max",
                "brand": "Apple",
                "price": 2499.99,
                "original_price": 2699.99,
                "description": "Professional laptop with M3 Max chip for demanding workflows",
                "features": ["M3 Max chip", "16-inch Liquid Retina XDR", "Up to 22hrs battery", "Thunderbolt 4"],
                "specs": {
                    "processor": "Apple M3 Max",
                    "memory": "36GB unified memory",
                    "storage": "512GB SSD",
                    "display": "16-inch Liquid Retina XDR",
                    "os": "macOS Sonoma"
                }
            },
            {
                "name": "Dell XPS 13 Plus",
                "brand": "Dell",
                "price": 1399.99,
                "description": "Ultra-thin Windows laptop with premium design and performance",
                "features": ["12th Gen Intel Core", "13.4-inch InfinityEdge", "Haptic trackpad", "Premium materials"],
                "specs": {
                    "processor": "Intel Core i7-1280P",
                    "memory": "16GB LPDDR5",
                    "storage": "512GB SSD",
                    "display": "13.4-inch FHD+",
                    "os": "Windows 11 Pro"
                }
            },
            {
                "name": "ASUS ROG Strix G16",
                "brand": "ASUS",
                "price": 1599.99,
                "description": "Gaming laptop with RTX 4070 and high refresh display",
                "features": ["RTX 4070 GPU", "165Hz display", "RGB keyboard", "Advanced cooling", "Gaming optimized"],
                "specs": {
                    "processor": "Intel Core i7-13650HX",
                    "gpu": "NVIDIA GeForce RTX 4070",
                    "memory": "16GB DDR5",
                    "storage": "1TB SSD",
                    "display": "16-inch FHD 165Hz"
                }
            }
        ]
    },
    
    "headphones": {
        "name": "Headphones & Audio",
        "description": "Premium headphones, earbuds, and audio equipment",
        "products": [
            {
                "name": "AirPods Pro (3rd Gen)",
                "brand": "Apple", 
                "price": 249.99,
                "description": "Premium wireless earbuds with active noise cancellation",
                "features": ["Active Noise Cancellation", "Spatial Audio", "MagSafe charging", "Sweat resistant"],
                "specs": {
                    "battery": "Up to 6 hours listening",
                    "connectivity": "Bluetooth 5.3",
                    "features": "ANC, Transparency mode",
                    "charging": "MagSafe, Lightning, Qi",
                    "compatibility": "iOS, Android"
                }
            },
            {
                "name": "Sony WH-1000XM5",
                "brand": "Sony",
                "price": 349.99,
                "original_price": 399.99,
                "description": "Industry-leading wireless noise canceling headphones",
                "features": ["Best-in-class ANC", "30hr battery", "Premium sound", "Comfortable design"],
                "specs": {
                    "battery": "Up to 30 hours",
                    "connectivity": "Bluetooth 5.2",
                    "driver": "30mm drivers",
                    "weight": "249g",
                    "charging": "USB-C quick charge"
                }
            },
            {
                "name": "Bose QuietComfort Ultra",
                "brand": "Bose",
                "price": 429.99,
                "description": "Premium noise canceling headphones with spatial audio",
                "features": ["World-class ANC", "Immersive Audio", "All-day comfort", "Premium materials"],
                "specs": {
                    "battery": "Up to 24 hours",
                    "connectivity": "Bluetooth 5.3",
                    "features": "Spatial Audio, ANC",
                    "weight": "254g",
                    "controls": "Touch controls"
                }
            }
        ]
    },
    
    "cameras": {
        "name": "Cameras & Photography",
        "description": "Digital cameras, lenses, and photography equipment",
        "products": [
            {
                "name": "Canon EOS R8",
                "brand": "Canon",
                "price": 1499.99,
                "description": "Full-frame mirrorless camera for content creators",
                "features": ["24.2MP full-frame sensor", "4K 60p video", "Dual Pixel CMOS AF", "Compact design"],
                "specs": {
                    "sensor": "24.2MP Full-Frame CMOS",
                    "video": "4K UHD 60p",
                    "autofocus": "Dual Pixel CMOS AF II",
                    "viewfinder": "2.36m-dot OLED EVF",
                    "connectivity": "Wi-Fi, Bluetooth"
                }
            },
            {
                "name": "Sony Alpha A7 IV",
                "brand": "Sony",
                "price": 2199.99,
                "description": "Professional hybrid camera for photo and video",
                "features": ["33MP full-frame", "4K 60p recording", "Real-time tracking", "5-axis stabilization"],
                "specs": {
                    "sensor": "33MP Full-Frame Exmor R",
                    "video": "4K 60p/120p",
                    "stabilization": "5-axis in-body",
                    "battery": "530 shots per charge",
                    "storage": "Dual SD slots"
                }
            },
            {
                "name": "Fujifilm X-T5",
                "brand": "Fujifilm",
                "price": 1699.99,
                "description": "APS-C mirrorless camera with film simulation modes",
                "features": ["40.2MP APS-C sensor", "Film simulation", "In-body stabilization", "Retro design"],
                "specs": {
                    "sensor": "40.2MP APS-C X-Trans CMOS 5 HR",
                    "video": "4K 60p",
                    "stabilization": "7-stop IBIS",
                    "battery": "740 shots per charge",
                    "design": "Weather-sealed body"
                }
            }
        ]
    },
    
    "smartwatches": {
        "name": "Smart Watches",
        "description": "Smartwatches and fitness trackers",
        "products": [
            {
                "name": "Apple Watch Series 9",
                "brand": "Apple",
                "price": 399.99,
                "description": "Most advanced Apple Watch with health monitoring",
                "features": ["S9 chip", "Double Tap gesture", "Precision Finding", "Health monitoring", "Always-On display"],
                "specs": {
                    "display": "45mm Always-On Retina",
                    "battery": "Up to 18 hours",
                    "health": "ECG, Blood Oxygen, Heart Rate",
                    "connectivity": "GPS + Cellular",
                    "os": "watchOS 10"
                }
            },
            {
                "name": "Samsung Galaxy Watch6",
                "brand": "Samsung",
                "price": 329.99,
                "description": "Android smartwatch with comprehensive health tracking",
                "features": ["Wear OS 4", "Health monitoring", "Sleep coaching", "Rotating bezel", "Always-on display"],
                "specs": {
                    "display": "44mm Super AMOLED",
                    "battery": "Up to 40 hours",
                    "health": "BioActive Sensor",
                    "storage": "16GB",
                    "os": "Wear OS 4"
                }
            },
            {
                "name": "Garmin Forerunner 965",
                "brand": "Garmin",
                "price": 599.99,
                "description": "Premium GPS running watch with AMOLED display",
                "features": ["AMOLED display", "Training metrics", "GPS accuracy", "Multi-band GNSS", "Music storage"],
                "specs": {
                    "display": "1.4-inch AMOLED",
                    "battery": "Up to 23 days",
                    "gps": "Multi-band GNSS",
                    "storage": "32GB for music",
                    "sports": "30+ sport profiles"
                }
            }
        ]
    },
    
    "gaming": {
        "name": "Gaming & Consoles", 
        "description": "Gaming consoles, controllers, and accessories",
        "products": [
            {
                "name": "PlayStation 5 Slim",
                "brand": "Sony",
                "price": 499.99,
                "description": "Latest PlayStation console with 4K gaming and ray tracing",
                "features": ["4K gaming", "Ray tracing", "3D audio", "DualSense controller", "Fast SSD loading"],
                "specs": {
                    "cpu": "AMD Zen 2 8-core",
                    "gpu": "AMD RDNA 2",
                    "storage": "1TB SSD",
                    "resolution": "Up to 4K 120Hz",
                    "audio": "3D Audio"
                }
            },
            {
                "name": "Xbox Series X",
                "brand": "Microsoft",
                "price": 499.99,
                "description": "Most powerful Xbox console with 4K gaming",
                "features": ["4K 120fps gaming", "Ray tracing", "Quick Resume", "Game Pass", "Backward compatibility"],
                "specs": {
                    "cpu": "AMD Zen 2 8-core 3.8GHz",
                    "gpu": "AMD RDNA 2 12 TFLOPS",
                    "storage": "1TB NVMe SSD",
                    "resolution": "Up to 4K 120fps",
                    "services": "Game Pass Ultimate"
                }
            },
            {
                "name": "Nintendo Switch OLED",
                "brand": "Nintendo",
                "price": 349.99,
                "description": "Hybrid console with vibrant OLED screen",
                "features": ["7-inch OLED screen", "Handheld/TV mode", "Enhanced audio", "Adjustable stand", "64GB storage"],
                "specs": {
                    "display": "7-inch OLED touchscreen",
                    "battery": "4.5-9 hours",
                    "storage": "64GB internal",
                    "connectivity": "Wi-Fi, Bluetooth",
                    "modes": "TV, Tabletop, Handheld"
                }
            }
        ]
    }
}

async def add_electronics_catalog():
    """Add electronics categories and products to the database"""
    print("🛍️ Adding Electronics Catalog to Database...")
    
    total_products = 0
    
    for category_id, category_data in ELECTRONICS_CATALOG.items():
        print(f"\n📱 Adding {category_data['name']} category...")
        
        for product_data in category_data['products']:
            # Create product document
            product = {
                "id": str(uuid.uuid4()),
                "name": product_data["name"],
                "brand": product_data["brand"],
                "price": product_data["price"],
                "original_price": product_data.get("original_price", product_data["price"]),
                "category": category_data["name"],
                "subcategory": category_id,
                "description": product_data["description"],
                "features": product_data["features"],
                "specs": product_data["specs"],
                "image_url": f"https://via.placeholder.com/400x400?text={product_data['name'].replace(' ', '+')}&bg=f0f0f0&color=333",
                "images": [
                    f"https://via.placeholder.com/400x400?text={product_data['name'].replace(' ', '+')}&bg=f0f0f0&color=333",
                    f"https://via.placeholder.com/400x400?text={product_data['name'].replace(' ', '+')}+Side&bg=f0f0f0&color=333",
                    f"https://via.placeholder.com/400x400?text={product_data['name'].replace(' ', '+')}+Back&bg=f0f0f0&color=333"
                ],
                "rating": round(4.0 + (hash(product_data["name"]) % 10) / 10, 1),  # Random rating 4.0-5.0
                "reviews_count": 50 + (hash(product_data["name"]) % 200),  # Random reviews 50-250
                "inventory": 100 + (hash(product_data["name"]) % 500),  # Random stock 100-600
                "is_active": True,
                "is_featured": hash(product_data["name"]) % 3 == 0,  # Randomly feature some products
                "tags": [
                    category_data["name"],
                    product_data["brand"],
                    category_id,
                    "electronics",
                    "new"
                ],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "ai_generated": True,
                "ai_description": f"This {product_data['name']} represents the latest in {category_data['name'].lower()} technology, combining cutting-edge features with premium build quality. Perfect for users who demand the best in performance and reliability."
            }
            
            # Check if product already exists
            existing = products_collection.find_one({"name": product["name"], "brand": product["brand"]})
            if existing:
                print(f"  ⏭️  Skipping {product['name']} (already exists)")
                continue
            
            # Insert product
            products_collection.insert_one(product)
            print(f"  ✅ Added {product['name']} - ${product['price']}")
            total_products += 1
    
    print(f"\n🎉 Successfully added {total_products} electronics products to the catalog!")
    print(f"📊 Database now contains {products_collection.count_documents({})} total products")
    
    # Display category summary
    print("\n📋 Category Summary:")
    for category_id, category_data in ELECTRONICS_CATALOG.items():
        count = products_collection.count_documents({"subcategory": category_id})
        print(f"  📱 {category_data['name']}: {count} products")

if __name__ == "__main__":
    asyncio.run(add_electronics_catalog())