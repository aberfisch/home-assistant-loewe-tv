"""Support for Loewe TV media player."""
import asyncio
import logging
from typing import Any

import voluptuous as vol
from wakeonlan import send_magic_packet
from zeep import Client
from zeep.exceptions import Fault, TransportError

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "loewe_tv"

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default="Loewe TV"): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Loewe TV platform."""
    host = config[CONF_HOST]
    mac = config[CONF_MAC]
    name = config[CONF_NAME]

    _LOGGER.debug("Setting up Loewe TV at %s", host)
    async_add_entities([LoeweTVMediaPlayer(hass, host, mac, name)], True)


class LoeweTVMediaPlayer(MediaPlayerEntity):
    """Representation of a Loewe TV."""

    def __init__(
        self, hass: HomeAssistant, host: str, mac: str, name: str
    ) -> None:
        """Initialize the Loewe TV device."""
        self._hass = hass
        self._host = host
        self._mac = mac
        self._name = name
        self._state = MediaPlayerState.OFF
        self._volume = 0
        self._is_volume_muted = False
        self._wsdl_url = f"http://{host}:8080/loewe/iControl/wsdl/iControlService.wsdl"
        self._client = None
        # Use MAC address as unique ID since it's unique per device
        self._attr_unique_id = mac.replace(":", "").lower()

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the device."""
        return self._attr_unique_id

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self) -> float:
        """Volume level of the media player (0..1)."""
        return self._volume / 100

    @property
    def is_volume_muted(self) -> bool:
        """Boolean if volume is currently muted."""
        return self._is_volume_muted

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
            | MediaPlayerEntityFeature.PLAY_MEDIA
        )

    def _send_soap_command(self, action: str, parameters: dict[str, Any] | None = None) -> Any:
        """Send a SOAP command to the TV."""
        try:
            # Create client if not cached or recreate on connection error
            if self._client is None:
                self._client = Client(self._wsdl_url)

            service = self._client.service

            if parameters:
                result = getattr(service, action)(**parameters)
            else:
                result = getattr(service, action)()

            _LOGGER.debug("SOAP command %s executed successfully", action)
            return result

        except TransportError as err:
            _LOGGER.error("Connection error to Loewe TV at %s: %s", self._host, err)
            self._state = MediaPlayerState.OFF
            # Reset client on connection error to force recreation
            self._client = None
            return None
        except Fault as err:
            _LOGGER.error("SOAP fault when calling %s: %s", action, err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error calling %s: %s", action, err)
            # Reset client on unexpected error to force recreation
            self._client = None
            return None

    async def async_update(self) -> None:
        """Retrieve the latest data from the TV."""
        _LOGGER.debug("Updating Loewe TV state")

        # Run SOAP commands in executor to avoid blocking
        result = await self._hass.async_add_executor_job(
            self._send_soap_command, "getPowerState"
        )

        if result is None:
            # TV is not reachable
            self._state = MediaPlayerState.OFF
            return

        # Parse power state
        if result == "ON":
            self._state = MediaPlayerState.ON
        elif result == "STANDBY":
            self._state = MediaPlayerState.STANDBY
        else:
            self._state = MediaPlayerState.OFF

        # Get volume information concurrently if TV is on
        if self._state == MediaPlayerState.ON:
            volume_task = self._hass.async_add_executor_job(
                self._send_soap_command, "getVolume"
            )
            mute_task = self._hass.async_add_executor_job(
                self._send_soap_command, "getMute"
            )

            volume_result, mute_result = await asyncio.gather(
                volume_task, mute_task, return_exceptions=True
            )

            if volume_result is not None and not isinstance(volume_result, Exception):
                try:
                    volume = int(volume_result)
                    if 0 <= volume <= 100:
                        self._volume = volume
                    else:
                        _LOGGER.error("Volume value out of range (0-100): %s", volume)
                except (ValueError, TypeError) as err:
                    _LOGGER.error("Invalid volume value received: %s (%s)", volume_result, err)

            if mute_result is not None and not isinstance(mute_result, Exception):
                try:
                    self._is_volume_muted = bool(mute_result)
                except (ValueError, TypeError) as err:
                    _LOGGER.error("Invalid mute value received: %s (%s)", mute_result, err)

    async def async_turn_on(self) -> None:
        """Turn the TV on using Wake-on-LAN."""
        _LOGGER.info("Turning on Loewe TV at %s using Wake-on-LAN", self._host)
        try:
            await self._hass.async_add_executor_job(send_magic_packet, self._mac)
        except Exception as err:
            _LOGGER.error("Failed to send Wake-on-LAN packet: %s", err)

    async def async_turn_off(self) -> None:
        """Turn the TV off."""
        _LOGGER.info("Turning off Loewe TV at %s", self._host)
        await self._hass.async_add_executor_job(
            self._send_soap_command, "setPowerState", {"state": "OFF"}
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        if not 0.0 <= volume <= 1.0:
            _LOGGER.error("Volume must be between 0.0 and 1.0, got: %s", volume)
            return

        volume_percent = int(volume * 100)
        _LOGGER.debug("Setting volume to %d%%", volume_percent)
        await self._hass.async_add_executor_job(
            self._send_soap_command, "setVolume", {"volume": volume_percent}
        )

    async def async_volume_up(self) -> None:
        """Increase volume by one step."""
        _LOGGER.debug("Increasing volume")
        await self._hass.async_add_executor_job(
            self._send_soap_command, "volumeUp"
        )

    async def async_volume_down(self) -> None:
        """Decrease volume by one step."""
        _LOGGER.debug("Decreasing volume")
        await self._hass.async_add_executor_job(
            self._send_soap_command, "volumeDown"
        )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the volume."""
        _LOGGER.debug("Setting mute to %s", mute)
        await self._hass.async_add_executor_job(
            self._send_soap_command, "setMute", {"mute": mute}
        )

    async def async_media_next_track(self) -> None:
        """Switch to the next channel."""
        _LOGGER.debug("Switching to next channel")
        await self._hass.async_add_executor_job(
            self._send_soap_command, "channelUp"
        )

    async def async_media_previous_track(self) -> None:
        """Switch to the previous channel."""
        _LOGGER.debug("Switching to previous channel")
        await self._hass.async_add_executor_job(
            self._send_soap_command, "channelDown"
        )

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        """Switch to a specific channel by number."""
        if media_type == "channel":
            try:
                channel = int(media_id)
                if 0 <= channel <= 999:
                    _LOGGER.info("Switching to channel %d", channel)
                    await self._hass.async_add_executor_job(
                        self._send_soap_command, "setChannel", {"channel": channel}
                    )
                else:
                    _LOGGER.error("Channel number must be between 0 and 999")
            except ValueError:
                _LOGGER.error("Invalid channel number: %s", media_id)
        else:
            _LOGGER.warning("Unsupported media type: %s", media_type)
