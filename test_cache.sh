#!/bin/bash
# Script de test du cache HTTP

echo "🧪 Test du système de cache"
echo "=============================="
echo ""

BASE_URL="http://localhost:4610"

# Liste des fichiers à tester
FILES=(
    "/index.html"
    "/liste_pays/style.css"
    "/liste_pays/index.php"
)

echo "📊 Étape 1: Premier accès (CACHE MISS attendu)"
echo "----------------------------------------------"
for file in "${FILES[@]}"; do
    echo -n "GET $file ... "
    curl -s -o /dev/null -w "Temps: %{time_total}s\n" "${BASE_URL}${file}"
    sleep 0.5
done

echo ""
echo "📊 Étape 2: Deuxième accès (CACHE HIT attendu)"
echo "-----------------------------------------------"
for file in "${FILES[@]}"; do
    echo -n "GET $file ... "
    curl -s -o /dev/null -w "Temps: %{time_total}s\n" "${BASE_URL}${file}"
    sleep 0.5
done

echo ""
echo "📊 Étape 3: Génération de trafic intensif"
echo "------------------------------------------"
echo "50 requêtes sur index.html..."
for i in {1..50}; do
    curl -s "${BASE_URL}/index.html" > /dev/null
done
echo "✅ Terminé"

echo ""
echo "📊 Étape 4: Statistiques du cache"
echo "----------------------------------"
curl -s "${BASE_URL}/_monitor/api" | python3 -c "
import sys, json
data = json.load(sys.stdin)
cache = data.get('cache', {})
print(f\"Hits: {cache.get('hits', 0)}\")
print(f\"Misses: {cache.get('misses', 0)}\")
print(f\"Hit Rate: {cache.get('hit_rate', '0%')}\")
print(f\"Cache Size: {cache.get('size', 0)}/{cache.get('capacity', 0)}\")
"

echo ""
echo "✅ Test terminé! Consultez le widget de monitoring sur ${BASE_URL}/"
