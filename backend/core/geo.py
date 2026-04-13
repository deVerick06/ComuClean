from math import radians, cos, sin, asin, sqrt

RAIO_MAXIMO_METROS = 100


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Retorna a distância em metros entre dois pontos GPS."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * asin(sqrt(a)) * 6_371_000
