from src.db.models import MenuCategory, MenuItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal

categories_data = [
{"name": "Kebaplar", "description": "Et ve mangal lezzetleri"},
{"name": "İçecekler", "description": "Sıcak ve soğuk içecekler"},
{"name": "Tatlılar", "description": "Geleneksel Türk tatlıları"},
]

items_data = [
{
"name": "Adana Kebap",
"description": "Acılı kıyma kebabı",
"price": Decimal("80.00"),
"category_name": "Kebaplar"
},
{
"name": "Künefe",
"description": "Tel kadayıf, peynir, şerbet",
"price": Decimal("40.00"),
"category_name": "Tatlılar"
},
{
"name": "Ayran",
"description": "Soğuk yoğurt içeceği",
"price": Decimal("15.00"),
"category_name": "İçecekler"
}
]

async def seed_menus(db: AsyncSession):
    # Kategorileri oluştur
    existing_categories = await db.execute(select(MenuCategory))
    existing_names = {c.name for c in existing_categories.scalars().all()}
    for cat in categories_data:
        if cat["name"] not in existing_names:
            db.add(MenuCategory(**cat))

    await db.commit()

    # Kategorilerle ilişkilendirerek ürünleri ekle
    for item in items_data:
        category_stmt = select(MenuCategory).where(MenuCategory.name == item["category_name"])
        result = await db.execute(category_stmt)
        category = result.scalars().first()

        if category:
            item_stmt = select(MenuItem).where(MenuItem.name == item["name"])
            item_exists = await db.execute(item_stmt)
            if not item_exists.scalars().first():
                db.add(MenuItem(
                    name=item["name"],
                    description=item["description"],
                    price=item["price"],
                    category_id=category.id
                ))

    await db.commit()