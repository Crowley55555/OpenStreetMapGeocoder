from osm_geocoder import osm_geocoder
# Прямое геокодирование: адрес → координаты + структурированный адрес
result_forward = osm_geocoder({
    "address": "Санкт-Петербург, Невский проспект, 5",
    "email": "lavrovartem0511@gmail.com",  # ← замените на ваш реальный email!
    "language": "ru"
})

print("📍 Прямое геокодирование:")
print(f"Адрес: {result_forward.get('address', '—')}")
print(f"Широта: {result_forward.get('latitude', '—')}")
print(f"Долгота: {result_forward.get('longitude', '—')}")
print(f"Индекс: {result_forward.get('postcode', '—')}")
print("-" * 50)

# Обратное геокодирование: координаты → адрес
result_reverse = osm_geocoder({
    "lat": 59.9366228,
    "lon": 30.3133837,
    "email": "lavrovartem0511@gmail.com",  # ← тот же email!
    "language": "ru"
})

print("🔄 Обратное геокодирование:")
print(f"Адрес: {result_reverse.get('address', '—')}")
print(f"Широта: {result_reverse.get('latitude', '—')}")
print(f"Долгота: {result_reverse.get('longitude', '—')}")
print(f"Индекс: {result_reverse.get('postcode', '—')}")