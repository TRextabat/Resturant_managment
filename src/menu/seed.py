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
"image_url": "http://localhost:8000/static/uploads/Bruschetta_al_Pomodoro.jpg"
},
{
"name": "Caprese Salad",
"description": "Mozzarella, domates, fesleğen ve balzamik glaze",
"price": Decimal("370.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8000/static/uploads/Caprese_Salad.jpg"
},
{
"name": "Arancini di Riso",
"description": "Peynir dolgulu kızarmış risotto topları",
"price": Decimal("370.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8000/static/uploads/Arancini_di_Riso.jpg"
},
{
"name": "Carpaccio di Manzo",
"description": "İnce dilim dana eti, roka, parmesan ve limon sos",
"price": Decimal("560.00"),
"category_name": "ANTIPASTI",
"image_url": "http://localhost:8000/static/uploads/Carpaccio_di_Manzo.jpg"
},
{
"name": "Margherita",
"description": "Mozzarella, domates sosu ve taze fesleğen",
"price": Decimal("390.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8000/static/uploads/Margherita.jpg"
},
{
"name": "Diavola",
"description": "Baharatlı salam, mozzarella ve acı biber",
"price": Decimal("460.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8000/static/uploads/Diavola.jpg"
},
{
"name": "Quattro Formaggi",
"description": "Gorgonzola, parmesan, mozzarella, pecorino",
"price": Decimal("420.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8000/static/uploads/Quattro_Formaggi.jpg"
},
{
"name": "Capricciosa",
"description": "Mantar, zeytin, enginar, jambon ve mozzarella",
"price": Decimal("490.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8000/static/uploads/Capricciosa.jpg"
},
{
"name": "Pizza Tartufo",
"description": "Trüf yağı, mantar, mozzarella ve ricotta peyniri",
"price": Decimal("460.00"),
"category_name": "PIZZE",
"image_url": "http://localhost:8000/static/uploads/Pizza_Tartufo.jpg"
},
{
"name": "Spaghetti alla Carbonara",
"description": "Yumurta, pecorino, guanciale ve karabiber",
"price": Decimal("390.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8000/static/uploads/Spaghetti_alla_Carbonara.jpg"
},
{
"name": "Fettuccine Alfredo",
"description": "Krema, parmesan ve tereyağı",
"price": Decimal("420.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8000/static/uploads/Fettuccine_Alfredo.jpg"
},
{
"name": "Lasagna alla Bolognese",
"description": "Kat kat makarna, ragù ve beşamel sos",
"price": Decimal("470.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8000/static/uploads/Lasagna_alla_Bolognese.jpg"
},
{
"name": "Penne Arrabbiata",
"description": "Acı domates soslu sarımsaklı penne",
"price": Decimal("370.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8000/static/uploads/Penne_Arrabbiata.jpg"
},
{
"name": "Tagliatelle al Pesto",
"description": "Fesleğenli pesto, çam fıstığı, parmesan",
"price": Decimal("460.00"),
"category_name": "PASTE",
"image_url": "http://localhost:8000/static/uploads/Tagliatelle_al_Pesto.jpg"
},
{
"name": "Pollo alla Parmigiana",
"description": "Pane edilmiş tavuk, domates sos ve eritilmiş mozzarella",
"price": Decimal("420.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8000/static/uploads/Pollo_alla_Parmigiana.jpg"
},
{
"name": "Saltimbocca alla Romana",
"description": "Dana eti, prosciutto ve adaçayı",
"price": Decimal("670.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8000/static/uploads/Saltimbocca_alla_Romana.jpg"
},
{
"name": "Branzino al Forno",
"description": "Fırında levrek, limon ve zeytinyağı ile",
"price": Decimal("720.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8000/static/uploads/Branzino_al_Forno.jpg"
},
{
"name": "Osso Buco",
"description": "Sebzeli dana incik, gremolata ile servis edilir",
"price": Decimal("690.00"),
"category_name": "SECONDI",
"image_url": "http://localhost:8000/static/uploads/Osso_Buco.jpg"
},
{
"name": "Insalata Mista",
"description": "Mevsim yeşillikleri",
"price": Decimal("290.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8000/static/uploads/Insalata_Mista.jpg"
},
{
"name": "Patate al Rosmarino",
"description": "Fırınlanmış biberiyeli patates",
"price": Decimal("290.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8000/static/uploads/Patate_al_Rosmarino.jpg"
},
{
"name": "Verdure Grigliate",
"description": "Izgara sebzeler",
"price": Decimal("240.00"),
"category_name": "CONTORNI",
"image_url": "http://localhost:8000/static/uploads/Verdure_Grigliate.jpg"
},
{
"name": "Tiramisu",
"description": "Mascarpone, espresso ve kakao",
"price": Decimal("240.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8000/static/uploads/Tiramisu.jpg"
},
{
"name": "Panna Cotta",
"description": "Vanilyalı krema tatlısı, orman meyveli sosla",
"price": Decimal("220.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8000/static/uploads/Panna_Cotta.jpg"
},
{
"name": "Cannoli Siciliani",
"description": "Ricotta dolgulu çıtır hamur",
"price": Decimal("220.00"),
"category_name": "DOLCI",
"image_url": "http://localhost:8000/static/uploads/Cannoli_Siciliani.jpg"
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