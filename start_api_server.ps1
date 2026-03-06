# Script de démarrage pour l'API web d'alertes solaires
# Lance le serveur Flask avec l'interface de démonstration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   API Web Alertes Solaires - COA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si l'environnement conda est activé
$envName = $env:CONDA_DEFAULT_ENV
if ($envName) {
    Write-Host "✓ Environnement conda actif: $envName" -ForegroundColor Green
} else {
    Write-Host "⚠ Aucun environnement conda détecté" -ForegroundColor Yellow
    Write-Host "  Activation de l'environnement recommandé..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Démarrage du serveur API..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Une fois démarré, accédez à:" -ForegroundColor White
Write-Host "  - Interface web: http://localhost:5000/" -ForegroundColor Cyan
Write-Host "  - API status:    http://localhost:5000/api/status" -ForegroundColor Cyan
Write-Host "  - API history:   http://localhost:5000/api/history" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur
python "$PSScriptRoot\scripts\solar_alert_api.py"
