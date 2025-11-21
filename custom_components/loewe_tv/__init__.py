"""The Loewe TV integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Loewe TV component from YAML configuration."""
    _LOGGER.debug("Setting up Loewe TV integration")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Loewe TV from a config entry."""
    _LOGGER.debug("Setting up Loewe TV config entry")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Loewe TV config entry")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
