#AutoSolarActivid

> ⚠️ **This repository is no longer in production.**
>
> The solar activity video and alert generation system has been integrated into the **Cosmic On Air** project.

> This repository is maintained for archive purposes.

>
> - 🌐 Official website: [cosmic-on-air.org](https://cosmic-on-air.org/)
> - 📦 Production repository: [github.com/Cosmic-On-Air/COA-AutoSolarActivid](https://github.com/Cosmic-On-Air/COA-AutoSolarActivid)

---

## About this project

AutoSolarActivid is an automated system that:

- generates **daily and weekly** videos of solar activity (NOAA/SOHO data)
- detects **proton flux anomalies** and sends alerts (Discord, email)
- automatically publishes videos to **YouTube**
- archives proton data in JSON format

## Project structure

| Folder / File | Role |

|---|---|

| `scripts/` | Python Scripts (Videos, Alerts, YouTube) |

| `solar_activity_videos/` | Generated Videos |

| `Protons/` | NOAA GOES Data (JSON Proton Stream) |

| `requirements.txt` | Python Dependencies |

| `.github/workflows/` | GitHub Actions Automation |

| `alert_config.json` | Alert Threshold Configuration |

## General Functionality

### Solar Videos
- **Daily**: `scripts/autovideo_daily.py` generates a video with the previous day's SOHO/NOAA data, with an embedded audio track (*Travelers* — Andrew Prahlow).

- **Weekly**: `scripts/autovideo_weekly.py` generates a weekly summary (without audio).

- Videos are automatically published to YouTube via `scripts/upload_youtube.py`.

### Solar Alerts
- `scripts/solar_alert_system.py` queries the NOAA API hourly (via GitHub Actions).

- An alert is triggered if the GOES proton flux exceeds a NOAA threshold:

| Level | Threshold | Impact |

|--------|-------|--------|
| S1 Minor | ≥ 10 pfu | Low biological risk (astronauts) |

| S2 Moderate | ≥ 100 pfu | High-altitude radiation risk |

| S3 High | ≥ 1,000 pfu | Radio interference at the poles |

| S4 Severe | ≥ 10,000 pfu | Polar flight and satellite risks |

| S5 Extreme | ≥ 100,000 pfu | Critical Emergency |

- In case of an alert, a notification is sent on **Discord** (`DISCORD_WEBHOOK_URL`) and the `CURRENT_SOLAR_ALERT.txt` file is updated in the repository.

- Minimum alert level: **S2** by default (configurable in `alert_config.json`).

- Cooldown: **6 hours** between two alerts of the same level.

### Local API (Development Use)

```bash
# Start the Flask server
python scripts/solar_alert_api.py
# or on Windows:
.\start_api_server.ps1
```

Endpoints: `http://localhost:5000/api/status` · `/api/history` · `/api/thresholds`

## Data Sources

| Source | Data | Credit |

|--------|---------|--------|
| NOAA SWPC / GOES | Proton Flux | [services.swpc.noaa.gov](https://services.swpc.noaa.gov) |

| SOHO LASCO C2 | Solar Imaging | © NASA/ESA |

| NMDB | Ground Neutrons | [nmdb.eu](https://www.nmdb.eu) |

## License

MIT — see [LICENSE](LICENSE).
