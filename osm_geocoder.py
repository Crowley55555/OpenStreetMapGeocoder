import time
import requests
from urllib.parse import quote_plus

# Глобальный последний запрос (для rate limiting)
_last_request_time = 0

def osm_geocoder(arguments):
    global _last_request_time

    address = arguments.get('address')
    lat = arguments.get('lat')
    lon = arguments.get('lon')
    email = arguments.get('email', '').strip()
    language = arguments.get('language', 'ru')
    limit = arguments.get('limit', 1)
    detailed = arguments.get('detailed', False)  # возвращать полные данные?

    if not email or '@' not in email:
        return {"error": "Укажите корректный email в параметре 'email' (требуется Nominatim)"}

    has_address = bool(address and address.strip())
    has_coords = lat is not None and lon is not None

    if has_address == has_coords:
        return {"error": "Укажите ТОЛЬКО 'address' ИЛИ ТОЛЬКО 'lat' и 'lon'"}

    # Собираем строку для кэширования
    cache_key = f"{'addr:' + address if has_address else f'coord:{lat},{lon}'}|{language}|{limit}"

    # Ждём, если прошло <1 сек с последнего запроса
    now = time.time()
    if now - _last_request_time < 1.1:
        time.sleep(1.1 - (now - _last_request_time))
    _last_request_time = time.time()

    try:
        if has_address:
            url = (
                f"https://nominatim.openstreetmap.org/search?"
                f"format=json&q={quote_plus(address)}&accept-language={language}&limit={limit}&addressdetails=1"
            )
        else:
            url = (
                f"https://nominatim.openstreetmap.org/reverse?"
                f"format=json&lat={lat}&lon={lon}&accept-language={language}&addressdetails=1"
            )

        headers = {"User-Agent": f"GeocoderApp/1.0 ({email})"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if has_address:
            if not data:
                return {"error": "Адрес не найден"}
            results = []
            for item in data:
                addr = item.get('address', {})
                compact = f"{addr.get('road', '')} {addr.get('house_number', '')}".strip()
                if not compact:
                    compact = addr.get('city', '') or addr.get('town', '') or addr.get('country', '')
                full = ", ".join(filter(None, [
                    addr.get('country'),
                    addr.get('state'),
                    addr.get('city') or addr.get('town') or addr.get('village'),
                    addr.get('road'),
                    addr.get('house_number')
                ]))
                result = {
                    "address": full,
                    "latitude": float(item['lat']),
                    "longitude": float(item['lon']),
                    "postcode": addr.get('postcode'),
                    "country_code": addr.get('country_code')
                }
                if detailed:
                    result["raw"] = item
                results.append(result)
            return results[0] if limit == 1 else results

        else:
            if "error" in data:
                return {"error": "Объект не найден"}
            addr = data.get('address', {})
            full = ", ".join(filter(None, [
                addr.get('country'),
                addr.get('state'),
                addr.get('city') or addr.get('town') or addr.get('village'),
                addr.get('road'),
                addr.get('house_number')
            ]))
            result = {
                "address": full,
                "latitude": float(lat),
                "longitude": float(lon),
                "postcode": addr.get('postcode'),
                "country_code": addr.get('country_code')
            }
            if detailed:
                result["raw"] = data
            return result

    except Exception as e:
        return {"error": f"Ошибка: {str(e)}"}