"""Channel up/down button entities for Loewe TV."""
from homeassistant.components.button import ButtonEntity
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Register channel buttons linked to the configured media player."""
    async_add_entities([LoeweChannelButton(hass, entry, "up"), LoeweChannelButton(hass, entry, "down")])


class LoeweChannelButton(ButtonEntity):
    """Press the TV's channel step key through its existing media player."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, direction: str) -> None:
        self._hass = hass
        self._entry = entry
        self._direction = direction
        self._attr_name = "Loewe TV Sender " + ("P+" if direction == "up" else "P−")
        self._attr_unique_id = f"{entry.entry_id}_channel_{direction}"
        self._attr_icon = "mdi:chevron-up" if direction == "up" else "mdi:chevron-down"

    async def async_press(self) -> None:
        """Call the working next/previous track action on the media player."""
        from homeassistant.const import CONF_MAC
        registry = er.async_get(self._hass)
        player_unique_id = self._entry.data[CONF_MAC].replace(":", "").lower()
        entity_id = registry.async_get_entity_id(MEDIA_PLAYER_DOMAIN, "loewe_tv", player_unique_id)
        if entity_id is None:
            raise RuntimeError("Loewe TV media player entity not found")
        service = "media_next_track" if self._direction == "up" else "media_previous_track"
        await self._hass.services.async_call(
            MEDIA_PLAYER_DOMAIN, service, {"entity_id": entity_id}, blocking=True
        )
