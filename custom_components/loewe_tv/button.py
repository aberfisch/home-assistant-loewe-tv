"""Channel up/down button entities for Loewe TV."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .media_player import LoeweTVMediaPlayer, RC_KEY_CHANNEL_UP, RC_KEY_CHANNEL_DOWN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Register two channel buttons linked to the configured TV."""
    async_add_entities([LoeweChannelButton(hass, entry, "up"), LoeweChannelButton(hass, entry, "down")])


class LoeweChannelButton(ButtonEntity):
    """Press the TV's channel step key."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, direction: str) -> None:
        self._hass = hass
        self._entry = entry
        self._direction = direction
        self._attr_name = "Loewe TV Sender " + ("P+" if direction == "up" else "P−")
        self._attr_unique_id = f"{entry.entry_id}_channel_{direction}"
        self._attr_icon = "mdi:chevron-up" if direction == "up" else "mdi:chevron-down"

    async def async_press(self) -> None:
        """Invoke the existing media-player channel action."""
        from homeassistant.const import CONF_MAC, CONF_HOST, CONF_NAME, CONF_PORT
        from .media_player import DEFAULT_PORT
        data = self._entry.data
        player = LoeweTVMediaPlayer(
            self._hass, data[CONF_HOST], data[CONF_MAC],
            data.get(CONF_NAME, "Loewe TV"), data.get(CONF_PORT, DEFAULT_PORT),
            self._entry.entry_id,
        )
        code = RC_KEY_CHANNEL_UP if self._direction == "up" else RC_KEY_CHANNEL_DOWN
        await self._hass.async_add_executor_job(player._inject_rc_key, code)
