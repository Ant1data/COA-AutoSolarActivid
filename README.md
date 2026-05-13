# AutoSolarActivid

> ⚠️ **Ce dépôt n'est plus en production.**
>
> Le système de génération de vidéos et d'alertes d'activité solaire a été intégré au projet **Cosmic On Air**.
> Ce dépôt est conservé à titre d'archive.
>
> - 🌐 Site officiel : [cosmic-on-air.org](https://cosmic-on-air.org/)
> - 📦 Dépôt de production : [github.com/Cosmic-On-Air/COA-AutoSolarActivid](https://github.com/Cosmic-On-Air/COA-AutoSolarActivid)

---

## À propos de ce projet

AutoSolarActivid est un système automatisé qui :
- génère des **vidéos quotidiennes et hebdomadaires** de l'activité solaire (données NOAA/SOHO)
- détecte les **anomalies de flux de protons** et envoie des alertes (Discord, email)
- publie automatiquement les vidéos sur **YouTube**
- archive les données protons au format JSON

## Structure du projet

| Dossier / Fichier | Rôle |
|---|---|
| `scripts/` | Scripts Python (vidéos, alertes, YouTube) |
| `solar_activity_videos/` | Vidéos générées |
| `Protons/` | Données NOAA GOES (flux de protons JSON) |
| `requirements.txt` | Dépendances Python |
| `.github/workflows/` | Automatisation GitHub Actions |
| `alert_config.json` | Configuration des seuils d'alerte |

## Fonctionnement général

### Vidéos solaires
- **Quotidien** : `scripts/autovideo_daily.py` génère une vidéo avec les données SOHO/NOAA du jour J-1, avec une piste audio embarquée (*Travelers* — Andrew Prahlow).
- **Hebdomadaire** : `scripts/autovideo_weekly.py` génère une synthèse de la semaine (sans audio).
- Les vidéos sont publiées automatiquement sur YouTube via `scripts/upload_youtube.py`.

### Alertes solaires
- `scripts/solar_alert_system.py` interroge l'API NOAA toutes les heures (via GitHub Actions).
- Une alerte est déclenchée si le flux de protons GOES dépasse un seuil NOAA :

| Niveau | Seuil | Impact |
|--------|-------|--------|
| S1 Mineur | ≥ 10 pfu | Risque biologique faible (astronautes) |
| S2 Modéré | ≥ 100 pfu | Risque radiation en haute altitude |
| S3 Fort | ≥ 1 000 pfu | Perturbations radio aux pôles |
| S4 Sévère | ≥ 10 000 pfu | Risques vols polaires et satellites |
| S5 Extrême | ≥ 100 000 pfu | Urgence critique |

- En cas d'alerte, une notification est envoyée sur **Discord** (`DISCORD_WEBHOOK_URL`) et le fichier `CURRENT_SOLAR_ALERT.txt` est mis à jour dans le dépôt.
- Niveau minimum d'alerte : **S2** par défaut (configurable dans `alert_config.json`).
- Cooldown : **6 heures** entre deux alertes du même niveau.

### API locale (usage développement)

```bash
# Lancer le serveur Flask
python scripts/solar_alert_api.py
# ou sous Windows :
.\start_api_server.ps1
```

Endpoints : `http://localhost:5000/api/status` · `/api/history` · `/api/thresholds`

## Sources de données

| Source | Données | Crédit |
|--------|---------|--------|
| NOAA SWPC / GOES | Flux de protons | [services.swpc.noaa.gov](https://services.swpc.noaa.gov) |
| SOHO LASCO C2 | Imagerie solaire | © NASA/ESA |
| NMDB | Neutrons au sol | [nmdb.eu](https://www.nmdb.eu) |

## Licence

MIT — voir [LICENSE](LICENSE).
