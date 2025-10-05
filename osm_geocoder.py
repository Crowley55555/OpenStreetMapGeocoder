def osm_geocoder(arguments):
    import requests
    from urllib.parse import quote_plus

    address = arguments.get('address')
    lat = arguments.get('lat')
    lon = arguments.get('lon')
    email = arguments.get('email', '').strip()

    if not email or '@' not in email:
        return {"error": "Укажите корректный email в параметре 'email' (требуется Nominatim)"}

    has_address = bool(address and address.strip())
    has_coords = lat is not None and lon is not None

    if has_address == has_coords:  # оба True или оба False
        return {"error": "Укажите ТОЛЬКО 'address' ИЛИ ТОЛЬКО 'lat' и 'lon'"}

    user_agent = f"MyGeocoderApp/1.0 ({email})"
    headers = {"User-Agent": user_agent}

    try:
        if has_address:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={quote_plus(address)}&accept-language=ru&limit=1&addressdetails=1"
        else:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&accept-language=ru&addressdetails=1"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        def format_addr(addr_dict):
            parts = []
            for key in ['country', 'state', 'city', 'town', 'village', 'road']:
                if addr_dict.get(key):
                    parts.append(addr_dict[key])
            if addr_dict.get('house_number'):
                if parts and 'road' in addr_dict:
                    parts[-1] += f" {addr_dict['house_number']}"
                else:
                    parts.append(addr_dict['house_number'])
            return ", ".join(parts) if parts else "Адрес недоступен"

        if has_address:
            if not data:
                return {"error": "Адрес не найден"}
            res = data[0]
            return {
                "address": format_addr(res.get('address', {})),
                "latitude": float(res['lat']),
                "longitude": float(res['lon'])
            }
        else:
            if "error" in data:
                return {"error": "Объект не найден"}
            return {
                "address": format_addr(data.get('address', {})),
                "latitude": float(lat),
                "longitude": float(lon)
            }

    except Exception as e:
        return {"error": f"Ошибка: {str(e)}"}