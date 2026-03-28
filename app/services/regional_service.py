"""
Regional service — loads and queries regional_matrix.json.
Provides regional context for any NS/PEI postal code prefix.
"""
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MATRIX_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "regional_matrix.json"

_matrix_cache: dict | None = None


def _load_matrix() -> dict:
    global _matrix_cache
    if _matrix_cache is None:
        try:
            _matrix_cache = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load regional matrix: {e}")
            _matrix_cache = {"regions": {}, "delivery_tiers": {}, "confidence_rules": {}}
    return _matrix_cache


def _extract_prefix(postal_code: str) -> str | None:
    """Extract the routing prefix from a Canadian postal code.
    NS: B followed by digit or 0+letter (B3, B0J, B0N, etc.)
    PEI: C followed by digit or 0+letter (C1A, C0A, C0B)
    """
    pc = postal_code.strip().upper().replace(" ", "")
    if not pc:
        return None

    # Check province
    if pc[0] not in ("B", "C"):
        return None

    # Try specific prefixes first (B0J, C0A, etc.), then broader (B3, B1)
    if len(pc) >= 3:
        prefix_3 = pc[:3]  # e.g., B0J, C1A
        matrix = _load_matrix()
        if prefix_3 in matrix.get("regions", {}):
            return prefix_3

    if len(pc) >= 2:
        prefix_2 = pc[:2]  # e.g., B3, B1, C0
        matrix = _load_matrix()
        if prefix_2 in matrix.get("regions", {}):
            return prefix_2

    return None


class RegionalContext:
    """Structured result from regional lookup."""

    def __init__(self, data: dict, prefix: str, confidence: str = "confirmed"):
        self.prefix = prefix
        self.name = data.get("name", "Unknown")
        self.nbc_reference = data.get("nbc_reference", "Unknown")
        self.hardiness_zone = data.get("hardiness_zone", "Unknown")

        # Snow/wind
        self.snow_load_kpa = data.get("snow_load_kpa")
        self.snow_load_psf = data.get("snow_load_psf")
        self.snow_load_confidence = data.get("snow_load_confidence", "unknown")
        self.rain_load_sr_kpa = data.get("rain_load_sr_kpa")
        self.frost_depth_in = data.get("frost_depth_in")

        # Season
        self.last_frost = data.get("last_frost")
        self.first_frost = data.get("first_frost")
        self.growing_season_days = data.get("growing_season_days", 0)
        self.persephone_start = data.get("persephone_start")
        self.persephone_end = data.get("persephone_end")
        self.persephone_days = data.get("persephone_days", 0)
        self.winter_solar_kwh = data.get("winter_solar_kwh_m2_day", 0)

        # Delivery
        self.delivery_tier = data.get("delivery_tier", 4)
        self.delivery_tier_name = data.get("delivery_tier_name", "Unknown")

        # Permits
        self.permit_authority = data.get("permit_authority", "Unknown")
        self.permit_threshold_m2 = data.get("permit_threshold_m2")
        self.permit_notes = data.get("permit_notes", "")

        # Support
        self.support_density = data.get("support_density", {})
        self.support_desert = self.support_density.get("support_desert", True)

        # Climate region
        self.climate_region = data.get("climate_region", "unknown")

        # Data confidence for this region
        self.data_confidence = confidence

    def to_dict(self) -> dict:
        return {
            "prefix": self.prefix,
            "name": self.name,
            "nbc_reference": self.nbc_reference,
            "hardiness_zone": self.hardiness_zone,
            "snow_load_kpa": self.snow_load_kpa,
            "snow_load_psf": self.snow_load_psf,
            "snow_load_confidence": self.snow_load_confidence,
            "frost_depth_in": self.frost_depth_in,
            "last_frost": self.last_frost,
            "first_frost": self.first_frost,
            "growing_season_days": self.growing_season_days,
            "persephone_days": self.persephone_days,
            "winter_solar_kwh": self.winter_solar_kwh,
            "delivery_tier": self.delivery_tier,
            "delivery_tier_name": self.delivery_tier_name,
            "permit_authority": self.permit_authority,
            "permit_notes": self.permit_notes,
            "support_desert": self.support_desert,
            "climate_region": self.climate_region,
            "data_confidence": self.data_confidence,
        }


def get_region(postal_code: str) -> tuple[Optional[RegionalContext], Optional[str]]:
    """Look up regional context for a postal code.

    Returns:
        (RegionalContext, None) on success
        (None, error_message) on failure
    """
    if not postal_code:
        return None, "Postal code is required"

    pc = postal_code.strip().upper()

    # Check province
    if not pc or pc[0] not in ("B", "C"):
        return None, f"Postal code '{postal_code}' is outside NS/PEI (must start with B or C)"

    prefix = _extract_prefix(pc)
    if prefix is None:
        return None, f"Postal code prefix for '{postal_code}' not found in regional matrix"

    matrix = _load_matrix()
    region_data = matrix.get("regions", {}).get(prefix)
    if region_data is None:
        return None, f"No regional data available for prefix '{prefix}'"

    # Determine overall data confidence
    snow_conf = region_data.get("snow_load_confidence", "unknown")
    rules = matrix.get("confidence_rules", {})

    if snow_conf == "confirmed":
        confidence = "confirmed"
    elif snow_conf == "corroborated":
        confidence = "corroborated"
    else:
        confidence = "estimated"

    ctx = RegionalContext(region_data, prefix, confidence)
    return ctx, None


def get_all_prefixes() -> list[str]:
    """Return all postal code prefixes in the regional matrix."""
    matrix = _load_matrix()
    return list(matrix.get("regions", {}).keys())


def get_confidence_cap(snow_confidence: str, distance_km: float = 0,
                       is_pei: bool = False) -> int:
    """Return the maximum confidence score based on data quality."""
    matrix = _load_matrix()
    rules = matrix.get("confidence_rules", {})

    if is_pei and snow_confidence != "confirmed":
        return rules.get("pei_unverified_cap", 50)

    if snow_confidence == "confirmed":
        return rules.get("confirmed_cap", 100)
    elif snow_confidence == "corroborated":
        return rules.get("corroborated_cap", 85)
    elif distance_km <= 100:
        return rules.get("estimated_within_100km_cap", 65)
    else:
        return rules.get("estimated_over_100km_cap", 45)
