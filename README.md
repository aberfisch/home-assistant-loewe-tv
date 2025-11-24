# Home Assistant Loewe TV Integration

A custom Home Assistant integration for controlling Loewe Television sets via their SOAP API. This plugin provides comprehensive control over your Loewe TV including power management, volume control, and channel switching.

## Features

### Power Management
- Check power status (TV reachable/not reachable)
- Turn TV on using Wake-on-LAN
- Turn TV to standby via SOAP command
- Automatic state detection

### Volume Control
- Get current volume level
- Set volume to specific level (0-99)
- Volume up/down controls via remote control keys
- Mute and unmute functionality

### Channel Control
- Switch to next channel (Channel Up) via remote control keys
- Switch to previous channel (Channel Down) via remote control keys
- Switch to specific channel by number using ZapToMedia

## Installation

### HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Install "Loewe TV" from HACS
3. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/loewe_tv` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

This integration is configured through the Home Assistant UI only. YAML configuration is not supported.

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click the **+ ADD INTEGRATION** button
3. Search for "Loewe TV"
4. Follow the setup wizard:
   - Enter the IP address of your Loewe TV
   - Enter the MAC address for Wake-on-LAN
   - Enter the port number (default: 905, older models may use 8080)
   - Optionally customize the device name

You can later modify these settings by clicking **CONFIGURE** on the Loewe TV integration card.

### Configuration Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `Host` | Yes | IP address of your Loewe TV | - |
| `MAC Address` | Yes | MAC address for Wake-on-LAN (formats: AA:BB:CC:DD:EE:FF or AABBCCDDEEFF) | - |
| `Name` | No | Friendly name for the TV | "Loewe TV" |
| `Port` | No | Port number for SOAP API | 905 |

### TV Pairing (First Time Setup)

**Important:** When you first set up the integration, your Loewe TV will display a pairing request on screen.

1. After adding the integration in Home Assistant, look at your TV screen
2. You should see a pairing request from "Home Assistant"
3. **Accept the pairing request on your TV** using your remote control
4. The integration will automatically connect after you accept

The pairing only needs to be done once. The integration will remember the authentication and reconnect automatically in the future.

**Note:** If you don't see a pairing request:
- Make sure your TV is turned on
- Check that the IP address is correct
- Verify that port 905 is accessible (some models may use 8080)
- Check Home Assistant logs for any error messages

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
- TV's SOAP API endpoint must be accessible (typically on port 905, older models may use port 8080)
  - Default: `http://<TV_IP>:905/loewe_tablet_0001`
  - Older models may use: `http://<TV_IP>:8080/loewe_tablet_0001`

## Troubleshooting

### TV Not Responding
- Ensure the TV is on the same network as Home Assistant
- Verify the IP address in your configuration is correct
- **Check the port number**: Most Loewe TVs use port 905, but older models may use port 8080
- Check if the SOAP API is enabled on your TV
- Try accessing `http://<TV_IP>:905/loewe_tablet_0001` in a browser
  - If that doesn't work, try port 8080: `http://<TV_IP>:8080/loewe_tablet_0001`

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

## API Documentation

For detailed information about the Loewe TV SOAP API, refer to the official documentation:
- [Loewe TV API Documentation (PDF)](https://github.com/meaumeau/Loewe_TV_API/blob/main/Documention/remote_api_1.0.47_Loewe%20_OCR.pdf)

This documentation provides comprehensive details about available SOAP methods, parameters, and TV control capabilities.

### SOAP Operations Used

This integration uses the following SOAP operations from the Loewe TV WSDL (`http://<TV_IP>:<PORT>/loewe_tablet_0001`):

- **GetVolume** - Retrieves current volume level (0-99)
- **SetVolume** - Sets volume level
- **GetMute** - Retrieves current mute status
- **SetMute** - Sets mute status
- **Standby** - Puts TV into standby mode
- **InjectRCKey** - Sends remote control key presses for:
  - Volume Up (key 16)
  - Volume Down (key 17)
  - Channel Up (key 32)
  - Channel Down (key 33)
- **ZapToMedia** - Switches to a specific channel using media locator

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- Uses [zeep](https://github.com/mvantellingen/python-zeep) for SOAP communication
- Uses [wakeonlan](https://github.com/remcohaszing/pywakeonlan) for Wake-on-LAN functionality
