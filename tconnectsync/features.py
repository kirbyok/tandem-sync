from .secret import ENABLE_TESTING_MODES
import os

"""Supported synchronization features."""

BASAL = "BASAL"
BOLUS = "BOLUS"
IOB = "IOB"
BOLUS_BG = "BOLUS_BG"
CGM = "CGM"
PUMP_EVENTS = "PUMP_EVENTS"
PUMP_EVENTS_BASAL_SUSPENSION = "PUMP_EVENTS_BASAL_SUSPENSION"
PROFILES = "PROFILES"
CGM_ALERTS = "CGM_ALERTS"
DEVICE_STATUS = "DEVICE_STATUS"

DEFAULT_FEATURES = [
    BASAL,
    BOLUS,
    PUMP_EVENTS,
    PROFILES
]

ALL_FEATURES = [
    BASAL,
    BOLUS,
    IOB,
    PUMP_EVENTS,
    PUMP_EVENTS_BASAL_SUSPENSION,
    PROFILES,
    CGM,
    CGM_ALERTS,
    DEVICE_STATUS,
]

# These modes are not yet ready for wide use.
if ENABLE_TESTING_MODES:
    ALL_FEATURES += [
        BOLUS_BG
    ]

# Override default features with env FEATURES if set
FEATURES_ENV = os.getenv("FEATURES")
if FEATURES_ENV:
    DEFAULT_FEATURES = [f.strip() for f in FEATURES_ENV.split(",") if f.strip()]