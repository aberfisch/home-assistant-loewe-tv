"""The Loewe TV integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Loewe TV component from YAML configuration."""
    _LOGGER.debug("Setting up Loewe TV integration")
    # Initialize domain data
    hass.data.setdefault(DOMAIN, {})
    
    # YAML platform configuration is automatically handled by Home Assistant
    # when it finds "platform: loewe_tv" under media_player in configuration.yaml
    # The async_setup_platform function in media_player.py will be called automatically
    
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
