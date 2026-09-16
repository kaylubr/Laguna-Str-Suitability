import numpy as np

from str_suitability.config import EARTH_RADIUS_KM


def haversine_km(
    longitude_a: np.ndarray | float,
    latitude_a: np.ndarray | float,
    longitude_b: np.ndarray | float,
    latitude_b: np.ndarray | float,
) -> np.ndarray:
    longitude_a_rad = np.radians(np.asarray(longitude_a, dtype=float))
    latitude_a_rad = np.radians(np.asarray(latitude_a, dtype=float))
    longitude_b_rad = np.radians(np.asarray(longitude_b, dtype=float))
    latitude_b_rad = np.radians(np.asarray(latitude_b, dtype=float))

    delta_latitude = latitude_b_rad - latitude_a_rad
    delta_longitude = longitude_b_rad - longitude_a_rad

    haversine_term = np.sin(delta_latitude / 2.0) ** 2 + (
        np.cos(latitude_a_rad) * np.cos(latitude_b_rad) * np.sin(delta_longitude / 2.0) ** 2
    )
    central_angle = 2.0 * np.arcsin(np.sqrt(np.clip(haversine_term, 0.0, 1.0)))
    return EARTH_RADIUS_KM * central_angle


def nearest_distance_km(
    origin_longitude: np.ndarray,
    origin_latitude: np.ndarray,
    target_longitude: np.ndarray,
    target_latitude: np.ndarray,
) -> np.ndarray:
    if len(target_longitude) == 0:
        return np.full(len(origin_longitude), np.nan)
    distances = haversine_km(
        origin_longitude[:, None],
        origin_latitude[:, None],
        target_longitude[None, :],
        target_latitude[None, :],
    )
    return distances.min(axis=1)
