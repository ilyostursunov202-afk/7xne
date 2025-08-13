#!/usr/bin/env python3
"""
Script to add medical equipment catalog from Albatros.uz to 7x marketplace
Categories: ИХЛА, Биохимия, Гемостаз, Гематология, Микробиология, ПЦР, Аллергология, КЩС, ВЭЖХ, Клинический анализ, Генетика
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
import uuid
import requests
from urllib.parse import urlparse

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client["ecommerce"]

def clear_existing_data():
    """Clear existing categories and products"""
    print("🗑️ Clearing existing data...")
    db.categories.delete_many({})
    db.products.delete_many({})
    print("✅ Data cleared")

def create_medical_categories():
    """Create medical equipment categories"""
    print("📂 Creating medical categories...")
    
    categories = [
        {
            "id": str(uuid.uuid4()),
            "name": "ИХЛА",
            "description": "Иммунохемилюминесцентный анализ - оборудование и реагенты для лабораторной диагностики",
            "image": "https://albatros.uz/image/product/eD4leHLltW.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Биохимия",
            "description": "Биохимические анализаторы для клинических лабораторий",
            "image": "https://albatros.uz/image/product/HlNOk0z9LF.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Гемостаз",
            "description": "Оборудование для исследования системы гемостаза и свертывания крови",
            "image": "https://albatros.uz/image/product/r25lhJVMOi.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Гематология",
            "description": "Гематологические анализаторы для исследования крови",
            "image": "https://albatros.uz/image/product/yYAwRLRmSd.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Микробиология",
            "description": "Микробиологические системы для культивирования и идентификации микроорганизмов",
            "image": "https://albatros.uz/image/product/duinH2NF5J.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ПЦР",
            "description": "ПЦР системы для молекулярной диагностики",
            "image": "https://albatros.uz/image/product/SHgg32RDAC.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Аллергология",
            "description": "Оборудование для диагностики аллергических заболеваний",
            "image": "https://albatros.uz/image/product/8EbjfRDN6B.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "КЩС",
            "description": "Анализаторы кислотно-щелочного состояния и газов крови",
            "image": "https://albatros.uz/image/product/mEByKAaVl7.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ВЭЖХ",
            "description": "Высокоэффективная жидкостная хроматография - анализаторы гемоглобина",
            "image": "https://albatros.uz/image/product/Q5KJRxaBjd.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Клинический анализ",
            "description": "Оборудование для клинических анализов мочи и других биологических жидкостей",
            "image": "https://albatros.uz/image/product/VI5RqxCLL4.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Генетика",
            "description": "Оборудование для генетических исследований и секвенирования",
            "image": "https://albatros.uz/image/product/dNs9h08PXG.webp",
            "parent_id": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
    ]
    
    # Insert categories
    result = db.categories.insert_many(categories)
    print(f"✅ Created {len(result.inserted_ids)} categories")
    
    # Return categories with their IDs for product assignment
    return {cat["name"]: cat["id"] for cat in categories}

def create_medical_products(category_ids):
    """Create medical products for each category"""
    print("🏥 Creating medical products...")
    
    products_data = {
        "ИХЛА": [
            {
                "name": "Maglumi 600",
                "description": "Для количественного анализа широкого спектра диагностических тестов с пропускной способностью для небольших лабораторий.",
                "price": 2500000,
                "image": "https://albatros.uz/image/product/eD4leHLltW.webp",
                "specifications": "Производительность: 60 тестов/час, Методы: CLIA, Объем пробы: 2-100 мкл"
            },
            {
                "name": "Maglumi 800",
                "description": "Для качественного и количественного анализа широкого спектра диагностических тестов с хорошей пропускной способностью.",
                "price": 3200000,
                "image": "https://albatros.uz/image/product/hHAcChXCdw.webp",
                "specifications": "Производительность: 120 тестов/час, Автоматическая загрузка реагентов"
            },
            {
                "name": "Maglumi X3",
                "description": "Ультра-производительное оборудование для количественного анализа широчайшего спектра диагностических тестов.",
                "price": 4500000,
                "image": "https://albatros.uz/image/product/BZukGGLWON.webp",
                "specifications": "Производительность: 180 тестов/час, Модульная система, AI-анализ"
            },
            {
                "name": "Maglumi X6",
                "description": "Для количественного анализа широкого спектра диагностических тестов: гормонов, онкомаркеров, ряда инфекций, показателей метаболизма, кардиомаркеров и ряда других анализов.",
                "price": 5800000,
                "image": "https://albatros.uz/image/product/ocpuTqOPqx.webp",
                "specifications": "Производительность: 240 тестов/час, 6 модулей, Широкая панель тестов"
            },
            {
                "name": "Maglumi X8",
                "description": "Для количественного анализа широчайшего спектра диагностических тестов.",
                "price": 7200000,
                "image": "https://albatros.uz/image/product/8E5YK28uky.webp",
                "specifications": "Производительность: 400 тестов/час, 8 модулей, Максимальная автоматизация"
            },
            {
                "name": "Реагенты ИХЛА",
                "description": "Реагенты для иммунохемилюминесцентного анализа",
                "price": 85000,
                "image": "https://albatros.uz/image/product/6g6QzPKwkL.webp",
                "specifications": "Различные тесты: гормоны, онкомаркеры, инфекции, кардиомаркеры"
            }
        ],
        "Биохимия": [
            {
                "name": "Biossays 240 Plus",
                "description": "Автоматический биохимический анализатор открытого типа",
                "price": 1850000,
                "image": "https://albatros.uz/image/product/HlNOk0z9LF.webp",
                "specifications": "240 тестов/час, Открытая система, 120 позиций для реагентов"
            },
            {
                "name": "Biossays E6",
                "description": "Полностью автоматическая новая эра решения iCa². Автоматический метод пункционного отбора проб, осуществляющий анаэробные измерения для обеспечения стабильности уровня ионизированного кальция и точности измерения",
                "price": 950000,
                "image": "https://albatros.uz/image/product/hoiA6Bmjfv.webp",
                "specifications": "Анализ электролитов, pH, газов крови, ионизированный кальций"
            },
            {
                "name": "Biossays C8",
                "description": "Анализатор, позволяющий вашей лаборатории реализовывать полную автоматизацию и максимальную эффективность, с мощной производительностью и модульной масштабируемостью",
                "price": 4200000,
                "image": "https://albatros.uz/image/product/7u7AJsJeeF.webp",
                "specifications": "800 тестов/час, Модульная система, ISE модуль, Автоматическое разведение"
            },
            {
                "name": "Biolumi CX8 (Биохимия + ИХЛА)",
                "description": "Новая полностью автоматическая модульная система Biolumi CХ8 сочетает высочайшую производительность, точность и простоту управления вашей лаборатории.",
                "price": 8500000,
                "image": "https://albatros.uz/image/product/RW4Nuc74PG.webp",
                "specifications": "Комбинированная система: 800 биохимических + 240 ИХЛА тестов/час"
            }
        ],
        "Гемостаз": [
            {
                "name": "ACL TOP 350 CTS",
                "description": "Настольная полностью автоматизированная система исследования гемостаза, с широкой панелью тестов, средней производительности.",
                "price": 3800000,
                "image": "https://albatros.uz/image/product/r25lhJVMOi.webp",
                "specifications": "90 тестов/час, Автоматическая загрузка образцов, CTS технология"
            },
            {
                "name": "Тромбоэластометр ROTEM delta",
                "description": "Получение статусного обзора коагулопатии в течение 10 минут помогает быстро идентифицировать скрытую коагулопатию и принять правильное решение для назначения индивидуализированного и целенаправленного лечения.",
                "price": 4500000,
                "image": "https://albatros.uz/image/product/frKsXMSBDt.webp",
                "specifications": "4 канала измерения, Результат за 10 минут, Point-of-care тестирование"
            }
        ],
        "Гематология": [
            {
                "name": "Dymind DF50 CRP",
                "description": "Автоматический гематологический анализатор 5-Diff",
                "price": 1200000,
                "image": "https://albatros.uz/image/product/yYAwRLRmSd.webp",
                "specifications": "5-Diff анализ, 60 образцов/час, CRP измерение, 23 параметра"
            },
            {
                "name": "Dymind DH26",
                "description": "Автоматический гематологический анализатор 3-Diff",
                "price": 850000,
                "image": "https://albatros.uz/image/product/v0pnskWIFx.webp",
                "specifications": "3-Diff анализ, 40 образцов/час, 20 параметров"
            },
            {
                "name": "Dymind DH-615",
                "description": "Автоматический гематологический анализатор 6-Diff с функцией подсчёта ретикулоцитов (RET) и с встроенным анализом с помощю искусственного интеллекта (AI)",
                "price": 2800000,
                "image": "https://albatros.uz/image/product/wO5xq2qwx1.webp",
                "specifications": "6-Diff + RET, 100 образцов/час, AI-анализ морфологии, 42 параметра"
            }
        ],
        "Микробиология": [
            {
                "name": "BD Bactec FX 40",
                "description": "Автоматизированная система для гемокультивирования. Система BD BACTEC™ FX 40 создана для ускоренного обнаружения бактерий и грибков в клинических образцах крови пациентов.",
                "price": 3200000,
                "image": "https://albatros.uz/image/product/duinH2NF5J.webp",
                "specifications": "40 флаконов, Автоматическое обнаружение роста, Встроенная встряхивалка"
            },
            {
                "name": "BD Phoenix M50",
                "description": "Автоматизированная микробиологическая система. Система для идентификации микроорганизмов и определения чувствительности к антимикробным препаратам Phoenix M50.",
                "price": 4800000,
                "image": "https://albatros.uz/image/product/gmzCmrA5IR.webp",
                "specifications": "50 панелей одновременно, ID + AST за 4-15 часов, База данных 680+ таксонов"
            }
        ],
        "ПЦР": [
            {
                "name": "Molecision R8",
                "description": "Полностью автоматизированная высокопроизводительная ПЦР «лаборатория».",
                "price": 5500000,
                "image": "https://albatros.uz/image/product/SHgg32RDAC.webp",
                "specifications": "96 образцов за цикл, Автоматическая подготовка, Real-time ПЦР"
            },
            {
                "name": "Molecision S6",
                "description": "Полностью интегрированная и закрытая цифровая ПЦР–система",
                "price": 3800000,
                "image": "https://albatros.uz/image/product/dGWl3Ux7X7.webp",
                "specifications": "6-канальная система, Цифровая ПЦР, Количественный анализ"
            },
            {
                "name": "Molecision MP-32",
                "description": "Система очистки нуклеиновых кислот Molecision MP-32",
                "price": 1800000,
                "image": "https://albatros.uz/image/product/cxJvo9D9JA.webp",
                "specifications": "32 образца за цикл, Магнитные частицы, Автоматическая экстракция"
            },
            {
                "name": "Molecision MP-96",
                "description": "Система очистки нуклеиновых кислот Molecision MP-96",
                "price": 2800000,
                "image": "https://albatros.uz/image/product/0sHSAH6KP3.webp",
                "specifications": "96 образцов за цикл, Высокая производительность, Различные типы образцов"
            }
        ],
        "Аллергология": [
            {
                "name": "Phadia 200",
                "description": "Полностью автоматизированный иммунофлюоресцентный анализатор для in-vitro диагностики аллергических, аутоиммунных и воспалительных заболеваний",
                "price": 4200000,
                "image": "https://albatros.uz/image/product/8EbjfRDN6B.webp",
                "specifications": "200 тестов/час, ImmunoCAP технология, 3000+ аллергенов"
            }
        ],
        "КЩС": [
            {
                "name": "GEM Premier 5000",
                "description": "Анализатор газов крови, pH, электролитов, гематокрита, лактата и глюкозы Gem Premier 5000",
                "price": 2200000,
                "image": "https://albatros.uz/image/product/mEByKAaVl7.webp",
                "specifications": "Полная панель КЩС, Результат за 1-2 минуты, iQM2 сенсоры"
            },
            {
                "name": "GEM Premier 3500",
                "description": "Анализатор газов крови, электролитов и метаболитов GEM Premier 3500",
                "price": 1800000,
                "image": "https://albatros.uz/image/product/67ksPtzvf2.webp",
                "specifications": "КЩС + электролиты + метаболиты, Компактный дизайн, iQM сенсоры"
            }
        ],
        "ВЭЖХ": [
            {
                "name": "Lifotronic H8",
                "description": "Автоматический анализатор гемоглобина Lifotronic H8",
                "price": 1500000,
                "image": "https://albatros.uz/image/product/Q5KJRxaBjd.webp",
                "specifications": "ВЭЖХ технология, HbA1c за 90 сек, 8 вариантов Hb"
            },
            {
                "name": "Lifotronic H9",
                "description": "Автоматический анализатор гемоглобина Lifotronic H9",
                "price": 1850000,
                "image": "https://albatros.uz/image/product/vhdYJoOIWt.webp",
                "specifications": "Усовершенствованная ВЭЖХ, HbA1c + β-талассемия, 120 образцов/час"
            },
            {
                "name": "Lifotronic GH-900 Plus",
                "description": "Автоматический анализатор гемоглобина Lifotronic GH-900 Plus",
                "price": 2200000,
                "image": "https://albatros.uz/image/product/H9FqsnG7t8.webp",
                "specifications": "Премиум ВЭЖХ система, 14 вариантов Hb, Высокая точность"
            }
        ],
        "Клинический анализ": [
            {
                "name": "URIT US-2000C",
                "description": "Модульная станция для полностью автоматизированного анализа мочи",
                "price": 2800000,
                "image": "https://albatros.uz/image/product/VI5RqxCLL4.webp",
                "specifications": "Химический + микроскопический анализ, 120 образцов/час, 15 параметров"
            }
        ],
        "Генетика": [
            {
                "name": "iSeq 100",
                "description": "Система секвенирования нового поколения (NGS) с технологией CMOS. Позволяет практически любой лаборатории получить мощную технологию NGS с низкой стоимостью секвенирования.",
                "price": 3500000,
                "image": "https://albatros.uz/image/product/dNs9h08PXG.webp",
                "specifications": "CMOS технология, SBS химия, до 4 млн ридов, локальный анализ"
            },
            {
                "name": "MiSeq i100 Series",
                "description": "Системы секвенирования MiSeq i100 и MiSeq i100 Plus устанавливают новые стандарты простоты и скорости при исключительной точности.",
                "price": 4800000,
                "image": "https://albatros.uz/image/product/LqmwFpQZyM.webp",
                "specifications": "До 25 млн ридов, гибкий рабочий процесс, 4-56 часов"
            },
            {
                "name": "MiniSeq",
                "description": "Мощное секвенирование с помощью Illumina в доступном исследовательском инструменте. Доступно в приобретении и экономично в эксплуатации.",
                "price": 2800000,
                "image": "https://albatros.uz/image/product/X9tfxenoLm.webp",
                "specifications": "До 7.5 млн ридов, кнопочное решение, ДНК и РНК секвенирование"
            },
            {
                "name": "NextSeq 550",
                "description": "Поддержка динамичных производственных мощностей и сокращение сроков выполнения работ благодаря опциям с высокой и средней производительности.",
                "price": 6800000,
                "image": "https://albatros.uz/image/product/yhpzTXQDkb.webp",
                "specifications": "До 400 млн ридов, кнопочное управление, быстрая загрузка"
            },
            {
                "name": "NextSeq 1000 & 2000",
                "description": "Универсальная платформа с гибкостью и масштабируемостью, позволяющая расширять возможности настольных приложений с XLEAP-SBS chemistry.",
                "price": 12500000,
                "image": "https://albatros.uz/image/product/AwDVZGRPEd.webp",
                "specifications": "До 1.1 млрд ридов, XLEAP-SBS, DRAGEN анализ"
            },
            {
                "name": "NovaSeq 6000",
                "description": "Соответствие выходных данных, времени получения результатов и стоимости образца потребностям исследования с настройкой метода секвенирования.",
                "price": 18500000,
                "image": "https://albatros.uz/image/product/YstOq6fL6s.webp",
                "specifications": "До 6 млрд ридов, различные проточные кюветы, высокая эффективность"
            },
            {
                "name": "NovaSeq X and X Plus",
                "description": "Исключительная пропускная способность и точность для проведения более масштабных исследований, амбициозных проектов и методов с большим объемом данных.",
                "price": 25000000,
                "image": "https://albatros.uz/image/product/z4vvBetVXW.webp",
                "specifications": "До 16 млрд ридов, лиофилизированные реагенты, минимальные отходы"
            },
            {
                "name": "iScan",
                "description": "Система Illumina iScan - современный сканер для быстрой, высокочувствительной и точной визуализации продуктов генетического анализа на основе массивов Illumina.",
                "price": 3200000,
                "image": "https://albatros.uz/image/product/QOdylJB7sT.webp",
                "specifications": "Infinium генотипирование, GWAS анализы, метилирование, BeadChip форматы"
            }
        ]
    }
    
    all_products = []
    for category_name, products in products_data.items():
        category_id = category_ids.get(category_name)
        if not category_id:
            print(f"⚠️ Category {category_name} not found")
            continue
            
        for product_data in products:
            product = {
                "id": str(uuid.uuid4()),
                "name": product_data["name"],
                "description": product_data["description"],
                "price": product_data["price"],
                "original_price": product_data["price"],
                "category_id": category_id,
                "category": category_name,
                "brand": "Medical Equipment",
                "images": [product_data["image"]],
                "specifications": product_data.get("specifications", ""),
                "stock": 10,
                "is_active": True,
                "seller_id": "admin",
                "tags": [category_name.lower(), "медицинское оборудование", "лабораторное оборудование"],
                "rating": 4.8,
                "reviews_count": 12,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            all_products.append(product)
    
    # Insert all products
    if all_products:
        result = db.products.insert_many(all_products)
        print(f"✅ Created {len(result.inserted_ids)} medical products")
    
    return len(all_products)

def create_sample_admin_user():
    """Create admin user if not exists"""
    print("👤 Checking admin user...")
    
    admin_user = db.users.find_one({"email": "admin@7x.com"})
    if not admin_user:
        admin_data = {
            "id": str(uuid.uuid4()),
            "email": "admin@7x.com",
            "name": "7x Administrator",
            "password": "$2b$12$LQv3c1yqBwlFdQcTXNYvN.kBWdhAP4NHAW6bDmk8/0nP8TuXvbG5e",  # password123
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "phone": "+998901234567",
            "phone_verified": True,
            "email_verified": True,
            "language": "en"
        }
        db.users.insert_one(admin_data)
        print("✅ Admin user created: admin@7x.com / password123")
    else:
        print("✅ Admin user already exists")

def main():
    """Main function to populate the medical catalog"""
    print("🏥 7x Medical Equipment Catalog Setup")
    print("=" * 50)
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Create medical categories
        category_ids = create_medical_categories()
        
        # Create medical products
        products_count = create_medical_products(category_ids)
        
        # Create admin user
        create_sample_admin_user()
        
        print("\n" + "=" * 50)
        print("🎉 Medical catalog setup completed!")
        print(f"📂 Categories: {len(category_ids)}")
        print(f"🏥 Products: {products_count}")
        print("🔑 Admin login: admin@7x.com / password123")
        print("\n✅ Your 7x medical marketplace is ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()