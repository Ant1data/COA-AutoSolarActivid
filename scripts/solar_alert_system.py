"""
Solar Activity Alert System
Detects abnormal solar activities and sends email alerts.

Alert thresholds based on NOAA standards:
- S1 (Minor): >=10 MeV flux > 10 pfu
- S2 (Moderate): >=10 MeV flux > 100 pfu
- S3 (Strong): >=10 MeV flux > 1000 pfu
- S4 (Severe): >=10 MeV flux > 10000 pfu
- S5 (Extreme): >=10 MeV flux > 100000 pfu
"""

import os
import json
import smtplib
from pathlib import Path
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Tuple, Optional
import requests

# Alert configuration (in protons·cm⁻²·s⁻¹·sr⁻¹)
ALERT_THRESHOLDS = {
    "S1_MINOR": 10,
    "S2_MODERATE": 100,
    "S3_STRONG": 1000,
    "S4_SEVERE": 10000,
    "S5_EXTREME": 100000
}

ALERT_LEVELS = {
    "S1_MINOR": {
        "name": "S1 - Minor",
        "color": "#FFD700",
        "description": "Minor biological risk for astronauts in EVA"
    },
    "S2_MODERATE": {
        "name": "S2 - Moderate",
        "color": "#FFA500",
        "description": "Increased radiation risk for high-altitude aircraft passengers"
    },
    "S3_STRONG": {
        "name": "S3 - Strong",
        "color": "#FF8C00",
        "description": "Possible HF radio disturbances in polar regions"
    },
    "S4_SEVERE": {
        "name": "S4 - Severe",
        "color": "#FF4500",
        "description": "Significant risks for polar flights and satellites"
    },
    "S5_EXTREME": {
        "name": "S5 - Extreme",
        "color": "#FF0000",
        "description": "⚠️ EMERGENCY LEVEL"
    }
}

# Base paths
ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "alert_config.json"
ALERT_LOG_FILE = ROOT / "alert_log.json"


class SolarAlertSystem:
    """Alert system for abnormal solar activities."""
    
    def __init__(self):
        self.config = self.load_config()
        self.alert_history = self.load_alert_history()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "recipients": ["recipient1@example.com"]
                },
                "alert_cooldown_hours": 6,
                "min_alert_level": "S2_MODERATE",
                "monitor_energies": [10, 50, 100]
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """Save configuration."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_alert_history(self) -> List[Dict]:
        """Charge l'historique des alertes."""
        if ALERT_LOG_FILE.exists():
            with open(ALERT_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_alert_history(self):
        """Sauvegarde l'historique des alertes."""
        with open(ALERT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.alert_history, f, indent=2)
    
    def fetch_current_proton_data(self) -> Optional[List[Dict]]:
        """Récupère les données actuelles de flux de protons depuis NOAA."""
        try:
            url = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-6-hour.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données: {e}")
            return None
    
    def analyze_data(self, data: List[Dict]) -> Dict[str, any]:
        """Analyse les données pour détecter les anomalies."""
        if not data:
            return {"alert": False}
        
        # Filtrer les énergies à surveiller
        monitor_energies = self.config.get("monitor_energies", [10, 50, 100])
        
        max_flux_by_energy = {}
        latest_readings = {}
        
        for entry in data:
            try:
                energy_str = entry.get("energy", "")
                if ">=" not in energy_str:
                    continue
                
                energy = float(energy_str.split(">=")[1].split()[0])
                
                if energy not in monitor_energies:
                    continue
                
                flux = float(entry.get("flux", 0))
                time_tag = entry.get("time_tag", "")
                
                if energy not in max_flux_by_energy or flux > max_flux_by_energy[energy]["flux"]:
                    max_flux_by_energy[energy] = {
                        "flux": flux,
                        "time": time_tag
                    }
                
                # Garder la lecture la plus récente
                if energy not in latest_readings or time_tag > latest_readings[energy]["time"]:
                    latest_readings[energy] = {
                        "flux": flux,
                        "time": time_tag
                    }
            except (ValueError, KeyError):
                continue
        
        # Déterminer le niveau d'alerte le plus élevé
        highest_alert = None
        alert_details = []
        
        for energy, reading in max_flux_by_energy.items():
            flux = reading["flux"]
            
            for threshold_key in reversed(list(ALERT_THRESHOLDS.keys())):
                threshold_value = ALERT_THRESHOLDS[threshold_key]
                
                if flux >= threshold_value:
                    alert_info = ALERT_LEVELS[threshold_key].copy()
                    alert_info["threshold_key"] = threshold_key
                    alert_info["energy"] = energy
                    alert_info["flux"] = flux
                    alert_info["time"] = reading["time"]
                    
                    alert_details.append(alert_info)
                    
                    if highest_alert is None or threshold_value > ALERT_THRESHOLDS[highest_alert]:
                        highest_alert = threshold_key
                    
                    break
        
        if highest_alert:
            return {
                "alert": True,
                "level": highest_alert,
                "level_name": ALERT_LEVELS[highest_alert]["name"],
                "details": alert_details,
                "latest_readings": latest_readings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "alert": False,
            "latest_readings": latest_readings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def should_send_alert(self, alert_level: str) -> bool:
        """Vérifie si une alerte doit être envoyée (cooldown)."""
        min_level = self.config.get("min_alert_level", "S2_MODERATE")
        min_threshold = ALERT_THRESHOLDS.get(min_level, 100)
        current_threshold = ALERT_THRESHOLDS.get(alert_level, 0)
        
        # Ne pas alerter si le niveau est trop faible
        if current_threshold < min_threshold:
            return False
        
        # Vérifier le cooldown
        cooldown_hours = self.config.get("alert_cooldown_hours", 6)
        
        for past_alert in reversed(self.alert_history):
            if past_alert.get("level") == alert_level:
                past_time = datetime.fromisoformat(past_alert.get("timestamp"))
                now = datetime.now(timezone.utc)
                hours_diff = (now - past_time).total_seconds() / 3600
                
                if hours_diff < cooldown_hours:
                    print(f"⏳ Cooldown actif: {hours_diff:.1f}h / {cooldown_hours}h")
                    return False
                break
        
        return True
    
    def send_email_alert(self, analysis: Dict) -> bool:
        """Envoie une alerte par email."""
        email_config = self.config.get("email", {})
        
        if not email_config.get("enabled", False):
            print("📧 Alertes email désactivées dans la configuration")
            return False
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🌞 ALERTE SOLAIRE - {analysis['level_name']}"
            msg['From'] = email_config["sender_email"]
            msg['To'] = ", ".join(email_config["recipients"])
            
            # Corps du message en texte et HTML
            text_body = self.create_text_email_body(analysis)
            html_body = self.create_html_email_body(analysis)
            
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envoyer l'email
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["sender_email"], email_config["sender_password"])
                server.send_message(msg)
            
            print(f"✅ Email d'alerte envoyé à {len(email_config['recipients'])} destinataire(s)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def create_text_email_body(self, analysis: Dict) -> str:
        """Crée le corps de l'email en texte brut."""
        body = f"""
╔══════════════════════════════════════╗
║   ALERTE D'ACTIVITÉ SOLAIRE ANORMALE  ║
╚══════════════════════════════════════╝

Niveau d'alerte: {analysis['level_name']}
Détecté le: {analysis['timestamp']}

═══════════════════════════════════════
DÉTAILS DES ANOMALIES:
═══════════════════════════════════════

"""
        for detail in analysis['details']:
            body += f"""
• Énergie: ≥{detail['energy']} MeV
  Flux: {detail['flux']:.2f} protons·cm⁻²·s⁻¹·sr⁻¹
  Niveau: {detail['name']}
  Impact: {detail['description']}
  Heure: {detail['time']}
"""
        
        body += f"""

═══════════════════════════════════════
LECTURES ACTUELLES:
═══════════════════════════════════════

"""
        for energy, reading in analysis['latest_readings'].items():
            body += f"• ≥{energy} MeV: {reading['flux']:.2f} pfu\n"
        
        body += """

Pour plus d'informations:
https://www.swpc.noaa.gov/

---
Message automatique du système de surveillance solaire
COA-AutoSolarActivid
"""
        return body
    
    def create_html_email_body(self, analysis: Dict) -> str:
        """Crée le corps de l'email en HTML."""
        level_color = ALERT_LEVELS[analysis['level']]['color']
        
        details_html = ""
        for detail in analysis['details']:
            details_html += f"""
            <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid {detail['color']}; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: {detail['color']};">
                    ⚡ {detail['name']} - ≥{detail['energy']} MeV
                </h3>
                <p style="margin: 5px 0;"><strong>Flux:</strong> {detail['flux']:.2f} protons·cm⁻²·s⁻¹·sr⁻¹</p>
                <p style="margin: 5px 0;"><strong>Impact:</strong> {detail['description']}</p>
                <p style="margin: 5px 0; color: #6c757d; font-size: 0.9em;"><strong>Détecté à:</strong> {detail['time']}</p>
            </div>
            """
        
        readings_html = ""
        for energy, reading in analysis['latest_readings'].items():
            readings_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">≥{energy} MeV</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">{reading['flux']:.2f} pfu</td>
            </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, {level_color} 0%, #ff6b6b 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🌞 ALERTE SOLAIRE
        </h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 20px; font-weight: bold;">
            {analysis['level_name']}
        </p>
    </div>
    
    <div style="background: white; padding: 30px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 8px 8px;">
        <p style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 0 0 20px 0; border-radius: 4px;">
            <strong>⏰ Détecté le:</strong> {analysis['timestamp']}
        </p>
        
        <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
            📊 Détails des anomalies détectées
        </h2>
        
        {details_html}
        
        <h2 style="color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; margin-top: 30px;">
            📈 Lectures actuelles
        </h2>
        
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Énergie</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Flux</th>
                </tr>
            </thead>
            <tbody>
                {readings_html}
            </tbody>
        </table>
        
        <div style="margin-top: 30px; padding: 20px; background: #e7f3ff; border-radius: 8px; text-align: center;">
            <p style="margin: 0 0 15px 0;">Pour plus d'informations sur l'activité solaire actuelle:</p>
            <a href="https://www.swpc.noaa.gov/" 
               style="display: inline-block; padding: 12px 24px; background: #0066cc; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Consulter NOAA SWPC
            </a>
        </div>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        
        <p style="text-align: center; color: #6c757d; font-size: 0.9em; margin: 0;">
            Message automatique du système de surveillance solaire<br>
            <strong>COA-AutoSolarActivid</strong>
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def log_alert(self, analysis: Dict):
        """Enregistre l'alerte dans l'historique."""
        log_entry = {
            "timestamp": analysis["timestamp"],
            "level": analysis["level"],
            "level_name": analysis["level_name"],
            "details": analysis["details"],
            "latest_readings": analysis["latest_readings"]
        }
        self.alert_history.append(log_entry)
        self.save_alert_history()
        print(f"📝 Alerte enregistrée dans l'historique")
    
    def check_and_alert(self) -> Dict:
        """Vérifie les données et envoie des alertes si nécessaire."""
        print("🔍 Vérification de l'activité solaire...")
        
        # Récupérer les données actuelles
        data = self.fetch_current_proton_data()
        
        if not data:
            return {"status": "error", "message": "Impossible de récupérer les données"}
        
        # Analyser les données
        analysis = self.analyze_data(data)
        
        if not analysis.get("alert"):
            print("✅ Activité solaire normale")
            return {"status": "ok", "message": "Pas d'anomalie détectée"}
        
        print(f"⚠️  ALERTE DÉTECTÉE: {analysis['level_name']}")
        
        # Vérifier si on doit envoyer une alerte
        if self.should_send_alert(analysis["level"]):
            # Envoyer l'email
            email_sent = self.send_email_alert(analysis)
            
            # Enregistrer l'alerte
            self.log_alert(analysis)
            
            return {
                "status": "alert_sent",
                "analysis": analysis,
                "email_sent": email_sent
            }
        else:
            print("⏭️  Alerte non envoyée (cooldown ou niveau insuffisant)")
            return {
                "status": "alert_suppressed",
                "analysis": analysis
            }


def main():
    """Point d'entrée principal du script."""
    import sys
    
    # Vérifier si on est en mode check-only (pour GitHub Actions)
    check_only = '--check-only' in sys.argv
    
    alert_system = SolarAlertSystem()
    
    if check_only:
        # Mode GitHub Actions: juste analyser sans envoyer d'emails
        print("🔍 Mode vérification activé (pas d'envoi d'email)")
        
        # Récupérer et analyser les données
        data = alert_system.fetch_current_proton_data()
        if not data:
            print("❌ Impossible de récupérer les données")
            sys.exit(1)
        
        analysis = alert_system.analyze_data(data)
        
        if analysis.get("alert"):
            print(f"\n🚨 ALERTE DÉTECTÉE !")
            print(f"Niveau: {analysis['level_name']}")
            print(f"\nDétails par énergie:")
            for detail in analysis['details']:
                print(f"  - ≥{detail['energy']} MeV: {detail['flux']:.2f} pfu")
                print(f"    Niveau: {detail['name']}")
                print(f"    Impact: {detail['description']}")
            sys.exit(1)  # Code de sortie non-zéro pour signaler une alerte
        else:
            print("\n✅ Aucune anomalie détectée dans l'activité solaire.")
            print("   Lectures actuelles:")
            for energy, reading in analysis.get('latest_readings', {}).items():
                print(f"   - ≥{energy} MeV: {reading['flux']:.2f} pfu")
            sys.exit(0)
    else:
        # Mode normal: analyser et envoyer des emails si nécessaire
        result = alert_system.check_and_alert()
        
        print("\n" + "="*50)
        print("RÉSULTAT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*50)


if __name__ == "__main__":
    main()

