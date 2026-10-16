"""The Loewe TV integration."""
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Loewe TV from a config entry."""
    _LOGGER.debug("Setting up Loewe TV config entry")
    card_path = Path(__file__).parent / 'www' / 'loewe-tv-card.js'
    await hass.http.async_register_static_paths([
        StaticPathConfig('/loewe_tv/loewe-tv-card.js', str(card_path), cache_headers=False)
    ])
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Loewe TV config entry")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
