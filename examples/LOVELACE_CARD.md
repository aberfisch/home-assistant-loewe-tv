# Loewe TV Lovelace card (experimental)

The custom card is bundled with the Loewe TV integration. It provides power, current channel, P+/P−, DVB-C channel selection, TV/Radio/HDMI source selection, mute and volume.

## Install in Home Assistant

1. Install this development version through a GitHub pre-release/HACS and restart Home Assistant.
2. Go to **Settings → Dashboards → Resources** (or dashboard edit menu → Resources).
3. Add resource URL `/loewe_tv/loewe-tv-card.js`, resource type **JavaScript module**.
4. Edit your dashboard → **Add card** → **Loewe TV** (or add a Manual card with the YAML below).
5. Hard refresh the browser if the card is not listed.

```yaml
type: custom:loewe-tv-card
entity: media_player.loewe_tv
title: Loewe Connect 48
```

Replace `media_player.loewe_tv` with your actual media-player entity ID. The card will try to find a Loewe media player automatically if `entity` is omitted.

**Note:** Home Assistant does not permit integrations to insert arbitrary controls into its standard device Controls panel. This is a separate Lovelace dashboard card. This is an untested development version for the SL320 chassis.
