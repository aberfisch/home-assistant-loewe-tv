# Home Assistant Loewe TV Integration

A custom Home Assistant integration for controlling Loewe Television sets via their SOAP API. This plugin provides comprehensive control over your Loewe TV including power management, volume control, and channel switching.

## Features

### Power Management
- Check power status (ON, OFF, or Standby)
- Turn TV on using Wake-on-LAN
- Turn TV off via SOAP command
- Automatic state detection

### Volume Control
- Get current volume level
- Set volume to specific level (0-100)
- Volume up/down controls
- Mute and unmute functionality

### Channel Control
- Switch to next channel (Channel Up)
- Switch to previous channel (Channel Down)
- Switch to specific channel by number (0-999)

## Installation

### HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Install "Loewe TV" from HACS
3. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/loewe_tv` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Option 1: UI Configuration (Recommended)

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click the **+ ADD INTEGRATION** button
3. Search for "Loewe TV"
4. Follow the setup wizard:
   - Enter the IP address of your Loewe TV
   - Enter the MAC address for Wake-on-LAN
   - Optionally customize the device name

You can later modify these settings by clicking **CONFIGURE** on the Loewe TV integration card.

### Option 2: YAML Configuration

Alternatively, add the following to your `configuration.yaml`:

```yaml
media_player:
  - platform: loewe_tv
    host: 192.168.1.100  # IP address of your Loewe TV
    mac: "AA:BB:CC:DD:EE:FF"  # MAC address for Wake-on-LAN
    name: "Living Room TV"  # Optional, defaults to "Loewe TV"
```

### Configuration Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `host` | Yes | IP address of your Loewe TV | - |
| `mac` | Yes | MAC address for Wake-on-LAN (formats: AA:BB:CC:DD:EE:FF or AABBCCDDEEFF) | - |
| `name` | No | Friendly name for the TV | "Loewe TV" |

## Usage

### Basic Controls
Once configured, your Loewe TV will appear as a media player entity in Home Assistant. You can control it through:
- The Home Assistant UI
- Automations
- Scripts
- Voice assistants (Alexa, Google Assistant)

### Services

#### Turn On
```yaml
service: media_player.turn_on
target:
  entity_id: media_player.living_room_tv
```

#### Turn Off
```yaml
service: media_player.turn_off
target:
  entity_id: media_player.living_room_tv
```

#### Set Volume (0.0 to 1.0)
```yaml
service: media_player.volume_set
target:
  entity_id: media_player.living_room_tv
data:
  volume_level: 0.5
```

#### Volume Up/Down
```yaml
service: media_player.volume_up
target:
  entity_id: media_player.living_room_tv
```

#### Mute/Unmute
```yaml
service: media_player.volume_mute
target:
  entity_id: media_player.living_room_tv
data:
  is_volume_muted: true
```

#### Channel Up/Down
```yaml
service: media_player.media_next_track
target:
  entity_id: media_player.living_room_tv
```

#### Switch to Specific Channel
```yaml
service: media_player.play_media
target:
  entity_id: media_player.living_room_tv
data:
  media_content_type: channel
  media_content_id: "24"
```

## Requirements

- Home Assistant 2023.1 or newer
- Loewe TV with SOAP API support (most models from 2010 onwards)
- TV and Home Assistant must be on the same network
- TV's SOAP API endpoint must be accessible at `http://<TV_IP>:8080/loewe/iControl/wsdl/iControlService.wsdl`

## Troubleshooting

### TV Not Responding
- Ensure the TV is on the same network as Home Assistant
- Verify the IP address in your configuration is correct
- Check if the SOAP API is enabled on your TV
- Try accessing `http://<TV_IP>:8080/loewe/iControl/wsdl/iControlService.wsdl` in a browser

### Wake-on-LAN Not Working
- Ensure Wake-on-LAN is enabled in your TV settings (usually in Network or Power settings)
- Verify the MAC address in your configuration is correct (check your router or TV network settings)
- Make sure your network allows broadcast packets (some routers block WOL across VLANs)
- The TV and Home Assistant must be on the same local network segment
- Some Loewe TVs require the TV to be in "Standby" mode rather than fully "Off" for WOL to work
- Try the integration's turn_on command - it automatically sends WOL packets to the broadcast address

### Check Logs
Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.loewe_tv: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- Uses [zeep](https://github.com/mvantellingen/python-zeep) for SOAP communication
- Uses [wakeonlan](https://github.com/remcohaszing/pywakeonlan) for Wake-on-LAN functionality
