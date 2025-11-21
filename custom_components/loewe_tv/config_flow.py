"""Config flow for Loewe TV integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def validate_mac(mac: str) -> str:
    """Validate and normalize MAC address."""
    # Remove common separators
    mac = mac.replace(":", "").replace("-", "").replace(".", "").upper()
    
    # Check if it's a valid MAC address (12 hex characters)
    if len(mac) != 12:
        raise vol.Invalid("MAC address must be 12 hexadecimal characters")
    
    try:
        int(mac, 16)
    except ValueError:
        raise vol.Invalid("MAC address must contain only hexadecimal characters")
    
    # Return in standard format with colons
    return ":".join(mac[i:i+2] for i in range(0, 12, 2))


class LoeweTVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loewe TV."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate MAC address format
                mac = validate_mac(user_input[CONF_MAC])
                user_input[CONF_MAC] = mac
                
                # Create unique ID based on MAC address
                unique_id = mac.replace(":", "").lower()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, f"Loewe TV {user_input[CONF_HOST]}"),
                    data=user_input,
                )
            except vol.Invalid as err:
                _LOGGER.error("Invalid MAC address: %s", err)
                errors["base"] = "invalid_mac"
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_MAC): str,
                vol.Optional(CONF_NAME, default="Loewe TV"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return LoeweTVOptionsFlow(config_entry)


class LoeweTVOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Loewe TV."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate MAC address format
                mac = validate_mac(user_input[CONF_MAC])
                user_input[CONF_MAC] = mac
                
                # Update the config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, **user_input},
                )
                
                return self.async_create_entry(title="", data={})
            except vol.Invalid as err:
                _LOGGER.error("Invalid MAC address: %s", err)
                errors["base"] = "invalid_mac"
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        # Get current values from config entry
        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_mac = self.config_entry.data.get(CONF_MAC, "")
        current_name = self.config_entry.data.get(CONF_NAME, "Loewe TV")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Required(CONF_MAC, default=current_mac): str,
                vol.Optional(CONF_NAME, default=current_name): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
