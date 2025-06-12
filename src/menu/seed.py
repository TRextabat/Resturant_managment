from src.db.models import MenuCategory, MenuItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal

categories_data = [
{"name": "ANTIPASTI", "description": "Başlangıçlar"},
{"name": "PIZZE", "description": "Odun Fırınında Pizza Çeşitleri"},
{"name": "PASTE", "description": "Makarna Çeşitleri"},
{"name": "SECONDI", "description": "Ana Yemekler"},
{"name": "CONTORNI", "description": "Yan Lezzetler"},
{"name": "DOLCI", "description": "Tatlılar"}
]

items_data = [
{
"name": "Bruschetta al Pomodoro",
"description": "Domates, sarımsak, fesleğen ve zeytinyağlı kızarmış ekmek",
"price": Decimal("340.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8500/static/uploads/Bruschetta_al_Pomodoro.jpeg"
},
{
"name": "Caprese Salad",
"description": "Mozzarella, domates, fesleğen ve balzamik glaze",
"price": Decimal("370.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8500/static/uploads/Caprese_Salad.jpeg"
},
{
"name": "Arancini di Riso",
"description": "Peynir dolgulu kızarmış risotto topları",
"price": Decimal("370.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8500/static/uploads/Arancini_di_Riso.jpeg"
},
{
"name": "Carpaccio di Manzo",
"description": "İnce dilim dana eti, roka, parmesan ve limon sos",
"price": Decimal("560.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8500/static/uploads/Carpaccio_di_Manzo.jpeg"
},
{
"name": "Margherita",
"description": "Mozzarella, domates sosu ve taze fesleğen",
"price": Decimal("390.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8500/static/uploads/Margherita.jpeg"
},
{
"name": "Diavola",
"description": "Baharatlı salam, mozzarella ve acı biber",
"price": Decimal("460.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8500/static/uploads/Diavola.jpeg"
},
{
"name": "Quattro Formaggi",
"description": "Gorgonzola, parmesan, mozzarella, pecorino",
"price": Decimal("420.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8500/static/uploads/Quattro_Formaggi.jpeg"
},
{
"name": "Capricciosa",
"description": "Mantar, zeytin, enginar, jambon ve mozzarella",
"price": Decimal("490.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8500/static/uploads/Capricciosa.jpeg"
},
{
"name": "Pizza Tartufo",
"description": "Trüf yağı, mantar, mozzarella ve ricotta peyniri",
"price": Decimal("460.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8500/static/uploads/Pizza_Tartufo.jpeg"
},
{
"name": "Spaghetti alla Carbonara",
"description": "Yumurta, pecorino, guanciale ve karabiber",
"price": Decimal("390.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8500/static/uploads/Spaghetti_alla_Carbonara.jpeg"
},
{
"name": "Fettuccine Alfredo",
"description": "Krema, parmesan ve tereyağı",
"price": Decimal("420.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8500/static/uploads/Fettuccine_Alfredo.jpeg"
},
{
"name": "Lasagna alla Bolognese",
"description": "Kat kat makarna, ragù ve beşamel sos",
"price": Decimal("470.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8500/static/uploads/Lasagna_alla_Bolognese.jpeg"
},
{
"name": "Penne Arrabbiata",
"description": "Acı domates soslu sarımsaklı penne",
"price": Decimal("370.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8500/static/uploads/Penne_Arrabbiata.jpeg"
},
{
"name": "Tagliatelle al Pesto",
"description": "Fesleğenli pesto, çam fıstığı, parmesan",
"price": Decimal("460.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8500/static/uploads/Tagliatelle_al_Pesto.jpeg"
},
{
"name": "Pollo alla Parmigiana",
"description": "Pane edilmiş tavuk, domates sos ve eritilmiş mozzarella",
"price": Decimal("420.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8500/static/uploads/Pollo_alla_Parmigiana.jpeg"
},
{
"name": "Saltimbocca alla Romana",
"description": "Dana eti, prosciutto ve adaçayı",
"price": Decimal("670.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8500/static/uploads/Saltimbocca_alla_Romana.jpeg"
},
{
"name": "Branzino al Forno",
"description": "Fırında levrek, limon ve zeytinyağı ile",
"price": Decimal("720.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8500/static/uploads/Branzino_al_Forno.jpeg"
},
{
"name": "Osso Buco",
"description": "Sebzeli dana incik, gremolata ile servis edilir",
"price": Decimal("690.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8500/static/uploads/Osso_Buco.jpeg"
},
{
"name": "Insalata Mista",
"description": "Mevsim yeşillikleri",
"price": Decimal("290.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8500/static/uploads/Insalata_Mista.jpeg"
},
{
"name": "Patate al Rosmarino",
"description": "Fırınlanmış biberiyeli patates",
"price": Decimal("290.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8500/static/uploads/Patate_al_Rosmarino.jpeg"
},
{
"name": "Verdure Grigliate",
"description": "Izgara sebzeler",
"price": Decimal("240.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8500/static/uploads/Verdure_Grigliate.jpeg"
},
{
"name": "Tiramisu",
"description": "Mascarpone, espresso ve kakao",
"price": Decimal("240.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8500/static/uploads/Tiramisu.jpeg"
},
{
"name": "Panna Cotta",
"description": "Vanilyalı krema tatlısı, orman meyveli sosla",
"price": Decimal("220.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8500/static/uploads/Panna_Cotta.jpeg"
},
{
"name": "Cannoli Siciliani",
"description": "Ricotta dolgulu çıtır hamur",
"price": Decimal("220.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8500/static/uploads/Cannoli_Siciliani.jpeg"
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
            result = await db.execute(item_stmt)  
            existing_item = result.scalars().first()  

            if not existing_item:  
                db.add(MenuItem(  
                    name=item["name"],  
                    description=item["description"],  
                    price=item["price"],  
                    category_id=category.id,  
                    image_url=item["image_url"]  
                ))  
            else:  
                # Güncelleme yapılacaksa  
                if not existing_item.image_url and item.get("image_url"):  
                    existing_item.image_url = item["image_url"]  
                    db.add(existing_item)  

    await db.commit()