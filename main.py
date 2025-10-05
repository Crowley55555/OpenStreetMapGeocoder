from osm_geocoder import osm_geocoder
# Прямое геокодирование: адрес → координаты
result1 = osm_geocoder({
    "address": "Санкт-Петербург, Невский проспект, 5",
    "email": "lavrovartem0511@gmail.com"  # рекомендуется
})
print(result1)

# Обратное геокодирование: координаты → адрес
result2 = osm_geocoder({
    "lat": 59.93428,
    "lon": 30.3351,
    "email": "lavrovartem0511@gmail.com"  # ← ОБЯЗАТЕЛЬНО укажите email и здесь!
})
print(result2)