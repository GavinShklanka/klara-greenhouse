"""Shared enums — single source of truth for valid string values."""

from __future__ import annotations

from enum import Enum


class Location(str, Enum):
    HALIFAX = "halifax"
    ANNAPOLIS_VALLEY = "annapolis_valley"
    SOUTH_SHORE = "south_shore"
    CAPE_BRETON = "cape_breton"
    NORTH_SHORE = "north_shore"
    CENTRAL_NS = "central_ns"
    EASTERN_SHORE = "eastern_shore"


class Goal(str, Enum):
    GROW_FOOD = "grow_food"
    SAVE_MONEY = "save_money"
    SUSTAINABILITY = "sustainability"
    MIXED = "mixed"


class Budget(str, Enum):
    UNDER_5K = "under_5k"
    FIVE_TO_TEN_K = "5k_10k"
    OVER_10K = "over_10k"


class PropertyType(str, Enum):
    BACKYARD = "backyard"
    RURAL = "rural"
    SMALL_LOT = "small_lot"
    NOT_SURE = "not_sure"


class GreenhouseType(str, Enum):
    POLYCARBONATE = "polycarbonate"
    POLYTUNNEL = "polytunnel"
    PASSIVE_SOLAR = "passive_solar"
    NOT_SURE = "not_sure"


class SolarExisting(str, Enum):
    NONE = "none"
    ROOFTOP = "rooftop"
    GROUND = "ground"
    NOT_SURE = "not_sure"


class ActionType(str, Enum):
    CHECKOUT = "checkout"
    QUOTE = "quote"
    CONSULTATION = "consultation"


class PlanTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class SessionStatus(str, Enum):
    INTAKE = "intake"
    PLAN = "plan"
    ACTION = "action"
    PAID = "paid"
