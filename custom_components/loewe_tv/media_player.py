"""Support for Loewe TV media player with authentication."""
import asyncio
import http.client
import logging
import random
import socket
import time
from typing import Any
import xml.etree.ElementTree as ET

from wakeonlan import send_magic_packet

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 905
NAMESPACE = "urn:loewe.de:RemoteTV:Tablet"

# WOL and retry settings
WOL_WAIT_TIME = 10  # Seconds to wait for TV to wake up after WOL
RETRY_DELAY = 3  # Seconds to wait between retry attempts
MAX_AUTH_RETRIES = 3  # Maximum authentication retry attempts

# Loewe TV remote control keycodes (alphabet: l2700)
RC_KEY_POWER = 12
RC_KEY_MUTE = 13
RC_KEY_VOLUME_UP = 16
RC_KEY_VOLUME_DOWN = 17
RC_KEY_CHANNEL_UP = 32
RC_KEY_CHANNEL_DOWN = 33


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loewe TV from a config entry."""
    host = entry.data[CONF_HOST]
    mac = entry.data[CONF_MAC]
    name = entry.data.get(CONF_NAME, "Loewe TV")
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    _LOGGER.debug("Setting up Loewe TV at %s:%s from config entry", host, port)
    async_add_entities([LoeweTVMediaPlayer(hass, host, mac, name, port, entry.entry_id)], True)


class LoeweTVMediaPlayer(MediaPlayerEntity):
    """Representation of a Loewe TV with authentication support."""

    def __init__(
        self, hass: HomeAssistant, host: str, mac: str, name: str, port: int = DEFAULT_PORT, entry_id: str | None = None
    ) -> None:
        """Initialize the Loewe TV device."""
        self._hass = hass
        self._host = host
        self._mac = mac
        self._name = name
        self._port = port
        self._entry_id = entry_id
        self._state = MediaPlayerState.OFF
        self._volume = 0
        self._is_volume_muted = False
        self._path = "/loewe_tablet_0001"
        
        # Authentication parameters
        self._fcid = str(random.randint(10000000, 99999999))
        self._client_id = None
        self._device_type = "HomeAssistant"
        self._device_name = "Home Assistant"
        self._device_uuid = mac  # Use MAC as device UUID
        self._requester_name = "Home Assistant Loewe TV Integration"
        
        # Use MAC address as unique ID since it's unique per device
        self._attr_unique_id = mac.replace(":", "").lower()
        
        # Set supported features using the _attr_ pattern for better Home Assistant compatibility
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
            | MediaPlayerEntityFeature.PLAY_MEDIA
        )

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the device."""
        return self._attr_unique_id

    @property
    def device_class(self) -> MediaPlayerDeviceClass:
        """Return the device class of the media player."""
        return MediaPlayerDeviceClass.TV

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

    def _send_wol(self) -> None:
        """Send a Wake-on-LAN magic packet to the TV."""
        try:
            # Calculate broadcast address from host IP
            ip_parts = self._host.split('.')
            if len(ip_parts) == 4:
                # Use the broadcast address for the /24 network
                broadcast_addr = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255"
                _LOGGER.debug("Sending WOL packet to MAC %s via broadcast %s", self._mac, broadcast_addr)
                send_magic_packet(self._mac, ip_address=broadcast_addr)
            else:
                # Fallback to sending without broadcast address
                _LOGGER.debug("Sending WOL packet to MAC %s", self._mac)
                send_magic_packet(self._mac)
        except Exception as err:
            _LOGGER.error("Failed to send Wake-on-LAN packet: %s", err)

    def _send_soap_request(self, soap_body: str, soap_action: str, retry_with_wol: bool = False) -> str | None:
        """Send a raw SOAP request to the TV.
        
        Args:
            soap_body: The SOAP request body
            soap_action: The SOAP action name
            retry_with_wol: If True, will send WOL and retry once on timeout
            
        Returns:
            Response text or None on failure
        """
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{NAMESPACE}#{soap_action}"'
        }
        
        try:
            conn = http.client.HTTPConnection(self._host, self._port, timeout=5)
            conn.request("POST", self._path, body=soap_body, headers=headers)
            response = conn.getresponse()
            resp_text = response.read().decode('utf-8', errors='ignore')
            conn.close()
            return resp_text
        except socket.timeout:
            _LOGGER.warning("Socket timeout connecting to TV at %s:%s", self._host, self._port)
            if retry_with_wol:
                _LOGGER.info("TV not reachable, sending WOL packet and retrying...")
                self._send_wol()
                # Wait for TV to wake up
                time.sleep(WOL_WAIT_TIME)
                # Retry once
                try:
                    conn = http.client.HTTPConnection(self._host, self._port, timeout=5)
                    conn.request("POST", self._path, body=soap_body, headers=headers)
                    response = conn.getresponse()
                    resp_text = response.read().decode('utf-8', errors='ignore')
                    conn.close()
                    return resp_text
                except Exception as err:
                    _LOGGER.error("Error sending SOAP request after WOL retry: %s", err)
                    return None
            return None
        except Exception as err:
            _LOGGER.error("Error sending SOAP request to %s:%s: %s", self._host, self._port, err)
            return None

    def _request_access(self, max_retries: int = MAX_AUTH_RETRIES, use_wol: bool = False) -> bool:
        """Request access to the TV and get ClientId.
        
        Args:
            max_retries: Maximum number of retry attempts for pending status
            use_wol: If True, send WOL and retry on timeout
            
        Returns:
            True if authentication succeeded, False otherwise
        """
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:RequestAccess>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:DeviceType>{self._device_type}</ltv:DeviceType>
              <ltv:DeviceName>{self._device_name}</ltv:DeviceName>
              <ltv:DeviceUUID>{self._device_uuid}</ltv:DeviceUUID>
              <ltv:RequesterName>{self._requester_name}</ltv:RequesterName>
            </ltv:RequestAccess>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        retry_count = 0
        while retry_count < max_retries:
            # Only use WOL if explicitly requested (e.g., during turn_on)
            resp_text = self._send_soap_request(soap_body, "RequestAccess", retry_with_wol=use_wol)
            if not resp_text:
                # If not using WOL and connection failed, don't retry - TV is likely off
                if not use_wol:
                    _LOGGER.debug("TV not reachable and WOL not requested, assuming TV is off")
                    return False
                _LOGGER.warning("Failed to get response for RequestAccess, retry %d/%d", retry_count + 1, max_retries)
                retry_count += 1
                time.sleep(RETRY_DELAY)
                continue
            
            try:
                root = ET.fromstring(resp_text)
                ns = {"ltv": NAMESPACE}
                status = root.find(".//ltv:AccessStatus", ns)
                clientid = root.find(".//ltv:ClientId", ns)
                
                if status is not None and clientid is not None:
                    status_text = status.text
                    if status_text == "Accepted":
                        self._client_id = clientid.text
                        _LOGGER.info("Successfully authenticated with TV, ClientId: %s", self._client_id)
                        return True
                    elif status_text == "Pending":
                        _LOGGER.warning("Pairing pending - please accept the pairing request on your TV (retry %d/%d)", retry_count + 1, max_retries)
                        retry_count += 1
                        time.sleep(RETRY_DELAY)
                        continue
                    elif status_text == "Denied":
                        _LOGGER.error("Pairing denied by TV")
                        return False
                    else:
                        _LOGGER.warning("Unexpected pairing status: %s", status_text)
                        retry_count += 1
                        time.sleep(RETRY_DELAY)
                        continue
                else:
                    _LOGGER.error("Missing status or clientid in response")
                    retry_count += 1
                    time.sleep(RETRY_DELAY)
                    continue
            except Exception as err:
                _LOGGER.error("Error parsing authentication response: %s", err)
                retry_count += 1
                time.sleep(RETRY_DELAY)
                continue
        
        _LOGGER.error("Failed to authenticate after %d retries", max_retries)
        return False

    def _ensure_authenticated(self, use_wol: bool = False) -> bool:
        """Ensure we have a valid ClientId, request access if needed.
        
        Args:
            use_wol: If True, send WOL and retry when TV is unreachable during authentication
            
        Returns:
            True if authenticated, False otherwise
        """
        if self._client_id is not None:
            return True
        return self._request_access(use_wol=use_wol)

    def _inject_rc_key(self, key_code: int, use_wol: bool = False) -> bool:
        """Send a remote control key press/release sequence.
        
        Args:
            key_code: The remote control key code to send
            use_wol: If True, send WOL and retry when TV is unreachable during this operation
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_authenticated(use_wol=use_wol):
            _LOGGER.error("Not authenticated, cannot send RC key")
            return False
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:InjectRCKey>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
              <ltv:InputEventSequence>
                <ltv:RCKeyEvent alphabet="l2700" value="{key_code}" mode="press"/>
                <ltv:RCKeyEvent alphabet="l2700" value="{key_code}" mode="release"/>
              </ltv:InputEventSequence>
            </ltv:InjectRCKey>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        # Use retry_with_wol based on the use_wol parameter
        resp_text = self._send_soap_request(soap_body, "InjectRCKey", retry_with_wol=use_wol)
        return resp_text is not None

    def _get_volume(self) -> int | None:
        """Get current volume level."""
        if not self._ensure_authenticated():
            return None
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:GetVolume>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
            </ltv:GetVolume>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "GetVolume")
        if not resp_text:
            return None
        
        try:
            root = ET.fromstring(resp_text)
            ns = {"ltv": NAMESPACE}
            value = root.find(".//ltv:Value", ns)
            if value is not None and value.text:
                return int(value.text)
        except Exception as err:
            _LOGGER.error("Error parsing volume response: %s", err)
        return None

    def _set_volume(self, volume: int) -> bool:
        """Set volume level (0-100)."""
        if not self._ensure_authenticated():
            return False
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:SetVolume>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
              <ltv:Value>{volume}</ltv:Value>
            </ltv:SetVolume>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "SetVolume")
        return resp_text is not None

    def _get_mute(self) -> bool | None:
        """Get current mute status."""
        if not self._ensure_authenticated():
            return None
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:GetMute>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
            </ltv:GetMute>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "GetMute")
        if not resp_text:
            return None
        
        try:
            root = ET.fromstring(resp_text)
            ns = {"ltv": NAMESPACE}
            value = root.find(".//ltv:Value", ns)
            if value is not None and value.text:
                return value.text.lower() == "true" or value.text == "1"
        except Exception as err:
            _LOGGER.error("Error parsing mute response: %s", err)
        return None

    def _set_mute(self, mute: bool) -> bool:
        """Set mute status."""
        if not self._ensure_authenticated():
            return False
        
        mute_value = "true" if mute else "false"
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:SetMute>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
              <ltv:Value>{mute_value}</ltv:Value>
            </ltv:SetMute>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "SetMute")
        return resp_text is not None

    def _standby(self) -> bool:
        """Put TV in standby mode."""
        if not self._ensure_authenticated():
            return False
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:Standby>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
            </ltv:Standby>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "Standby")
        return resp_text is not None

    def _zap_to_media(self, player: str, locator: str) -> bool:
        """Switch to a specific media channel."""
        if not self._ensure_authenticated():
            return False
        
        soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ltv="{NAMESPACE}">
          <soapenv:Header/>
          <soapenv:Body>
            <ltv:ZapToMedia>
              <ltv:fcid>{self._fcid}</ltv:fcid>
              <ltv:ClientId>{self._client_id}</ltv:ClientId>
              <ltv:Player>{player}</ltv:Player>
              <ltv:Locator>{locator}</ltv:Locator>
            </ltv:ZapToMedia>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        
        resp_text = self._send_soap_request(soap_body, "ZapToMedia")
        return resp_text is not None

    async def async_update(self) -> None:
        """Retrieve the latest data from the TV."""
        _LOGGER.debug("Updating Loewe TV state")

        # Try to get volume to check if TV is reachable/on
        volume = await self._hass.async_add_executor_job(self._get_volume)
        
        if volume is None:
            # TV is not reachable or authentication failed
            self._state = MediaPlayerState.OFF
            # Reset client_id to force re-authentication on next successful connection
            self._client_id = None
            return

        # TV is reachable, assume it's ON
        self._state = MediaPlayerState.ON
        self._volume = volume

        # Get mute status
        mute = await self._hass.async_add_executor_job(self._get_mute)
        if mute is not None:
            self._is_volume_muted = mute

    async def async_turn_on(self) -> None:
        """Turn the TV on using Wake-on-LAN and power RC key."""
        _LOGGER.info("Turning on Loewe TV at %s using Wake-on-LAN", self._host)
        await self._hass.async_add_executor_job(self._send_wol)
        # Wait for TV to wake up before attempting further operations
        _LOGGER.debug("Waiting %d seconds for TV to wake up...", WOL_WAIT_TIME)
        await asyncio.sleep(WOL_WAIT_TIME)
        # Send power RC key to ensure TV turns on from standby
        _LOGGER.debug("Sending power RC key to turn on TV")
        result = await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_POWER, True)
        if result:
            _LOGGER.debug("Power RC key sent successfully")
        else:
            _LOGGER.warning("Failed to send power RC key, TV may require manual power on")

    async def async_turn_off(self) -> None:
        """Turn the TV off using the Power RC key."""
        _LOGGER.info("Turning off Loewe TV at %s", self._host)
        await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_POWER)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        if not 0.0 <= volume <= 1.0:
            _LOGGER.error("Volume must be between 0.0 and 1.0, got: %s", volume)
            return

        volume_percent = int(volume * 100)
        _LOGGER.debug("Setting volume to %d%%", volume_percent)
        await self._hass.async_add_executor_job(self._set_volume, volume_percent)

    async def async_volume_up(self) -> None:
        """Increase volume by one step."""
        _LOGGER.debug("Increasing volume")
        await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_VOLUME_UP)

    async def async_volume_down(self) -> None:
        """Decrease volume by one step."""
        _LOGGER.debug("Decreasing volume")
        await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_VOLUME_DOWN)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the volume."""
        _LOGGER.debug("Setting mute to %s", mute)
        
        # Use cached mute state from last update
        # Note: async_update() is called regularly by Home Assistant, so this should be fresh
        current_mute = self._is_volume_muted
        
        # Only toggle if current state differs from desired state
        # RC_KEY_MUTE (13) is a toggle button, like on the physical remote
        if current_mute != mute:
            _LOGGER.debug("Current mute is %s, toggling to %s", current_mute, mute)
            success = await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_MUTE)
            # Update cached state only if the operation succeeded
            # Since we know the starting state and it's a toggle, we can infer the new state
            # The next async_update() will synchronize with the actual TV state
            if success:
                self._is_volume_muted = mute
            else:
                _LOGGER.warning("Failed to toggle mute state")
        else:
            _LOGGER.debug("Mute already at desired state %s", mute)

    async def async_media_next_track(self) -> None:
        """Switch to the next channel."""
        _LOGGER.debug("Switching to next channel")
        await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_CHANNEL_UP)

    async def async_media_previous_track(self) -> None:
        """Switch to the previous channel."""
        _LOGGER.debug("Switching to previous channel")
        await self._hass.async_add_executor_job(self._inject_rc_key, RC_KEY_CHANNEL_DOWN)

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        """Switch to a specific channel by number or locator."""
        if media_type == "channel":
            try:
                channel = int(media_id)
                if 0 <= channel <= 999:
                    _LOGGER.info("Switching to channel %d", channel)
                    # Use ZapToMedia with channel locator format
                    locator = f"dvb://{channel}"
                    await self._hass.async_add_executor_job(
                        self._zap_to_media, "MainVideo", locator
                    )
                else:
                    _LOGGER.error("Channel number must be between 0 and 999")
            except ValueError:
                _LOGGER.error("Invalid channel number: %s", media_id)
        else:
            _LOGGER.warning("Unsupported media type: %s", media_type)
