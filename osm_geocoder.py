def osm_geocoder(arguments):
    import time
    import requests
    from urllib.parse import quote_plus

    global _last_request_time
    if '_last_request_time' not in globals():
        globals()['_last_request_time'] = 0

    # Обязательные и опциональные параметры
    email = arguments.get('email')
    address = arguments.get('address')
    lat = arguments.get('lat')
    lon = arguments.get('lon')
    language = arguments.get('language', 'ru')  # по умолчанию 'ru'

    # Проверка обязательного параметра
    if not email or '@' not in str(email):
        return {"error": "Параметр 'email' обязателен и должен содержать '@'"}

    has_address = address is not None and address != ""
    has_coords = lat is not None and lon is not None

    if has_address and has_coords:
        return {"error": "Укажите либо 'address', либо 'lat' и 'lon', но не вместе."}
    if not has_address and not has_coords:
        return {"error": "Укажите либо 'address', либо оба параметра 'lat' и 'lon'."}

    # Rate limiting: 1 запрос в секунду
    now = time.time()
    if now - globals()['_last_request_time'] < 1.1:
        time.sleep(1.1 - (now - globals()['_last_request_time']))
    globals()['_last_request_time'] = now

    try:
        headers = {"User-Agent": f"GeocoderApp/1.0 ({email})"}

        if has_address:
            url = (
                f"https://nominatim.openstreetmap.org/search?"
                f"format=json&q={quote_plus(address)}&accept-language={language}&limit=1&addressdetails=1"
            )
        else:
            # Убран лишний пробел в URL
            url = (
                f"https://nominatim.openstreetmap.org/reverse?"
                f"format=json&lat={lat}&lon={lon}&accept-language={language}&addressdetails=1"
            )

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        def format_address(addr_dict):
            parts = []
            for key in ['country', 'state', 'city', 'town', 'village', 'road']:
                if addr_dict.get(key):
                    parts.append(addr_dict[key])
            if addr_dict.get('house_number') and parts:
                parts[-1] += f" {addr_dict['house_number']}"
            return ", ".join(parts) if parts else "Адрес недоступен"

        if has_address:
            if not data:
                return {"error": "Адрес не найден"}
            item = data[0]
            return {
                "address": format_address(item.get("address", {})),
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
                "postcode": item.get("address", {}).get("postcode"),
                "country_code": item.get("address", {}).get("country_code")
            }
        else:
            if "error" in data:
                return {"error": "Объект не найден"}
            return {
                "address": format_address(data.get("address", {})),
                "latitude": float(lat),
                "longitude": float(lon),
                "postcode": data.get("address", {}).get("postcode"),
                "country_code": data.get("address", {}).get("country_code")
            }

    except Exception as e:
        return {"error": f"Ошибка запроса: {str(e)}"}