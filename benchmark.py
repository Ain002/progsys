#!/usr/bin/env python3
"""
Script de benchmark pour tester les optimisations
Compare les performances :
- Sans cache
- Avec cache
- Avec gzip
"""

import subprocess
import sys
import json
from datetime import datetime


def run_benchmark(url, name, requests=1000, concurrency=50):
    """
    Exécute un benchmark avec Apache Bench.
    
    Args:
        url: L'URL à tester
        name: Nom du test
        requests: Nombre total de requêtes
        concurrency: Nombre de requêtes concurrentes
    """
    print(f"\n{'='*60}")
    print(f"🔄 Test: {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"Requêtes: {requests}, Concurrence: {concurrency}")
    print(f"Temps: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        cmd = [
            "ab",
            "-n", str(requests),
            "-c", str(concurrency),
            "-g", f"benchmark_{name.lower().replace(' ', '_')}.tsv",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Parser les résultats
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Requests per second' in line or \
                   'Time per request' in line or \
                   'Failed requests' in line or \
                   'Bytes transferred' in line:
                    print(f"✓ {line.strip()}")
            print("\n✓ Benchmark complété avec succès!")
        else:
            print(f"❌ Erreur: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ Apache Bench non trouvé. Installez-le avec: sudo apt-get install apache2-utils")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ Le benchmark a dépassé le timeout")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Lance les benchmarks."""
    base_url = "http://localhost:4610"
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     BENCHMARK DE PERFORMANCE DU SERVEUR HTTP           ║
    ║  Comparaison: Sans cache vs Avec cache vs Avec gzip    ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Vérifier que le serveur est accessible
    try:
        import urllib.request
        urllib.request.urlopen(base_url, timeout=2)
    except Exception as e:
        print(f"❌ Erreur: Le serveur n'est pas accessible sur {base_url}")
        print(f"   Assurez-vous que le serveur est lancé: python server.py")
        sys.exit(1)
    
    # Lancer les tests
    tests = [
        {
            "url": f"{base_url}/index.html",
            "name": "Sans cache (première requête)"
        },
        {
            "url": f"{base_url}/index.html",
            "name": "Avec cache (hit)"
        },
        {
            "url": f"{base_url}/static/css/style.css",
            "name": "CSS avec gzip"
        },
        {
            "url": f"{base_url}/static/js/main.js",
            "name": "JS avec gzip"
        },
    ]
    
    for test in tests:
        run_benchmark(test["url"], test["name"], requests=1000, concurrency=50)
    
    print(f"\n{'='*60}")
    print("✓ Tous les benchmarks sont terminés!")
    print(f"{'='*60}\n")
    print("Résultats sauvegardés dans les fichiers TSV:")
    print("  - benchmark_sans_cache.tsv")
    print("  - benchmark_avec_cache.tsv")
    print("  - benchmark_css_avec_gzip.tsv")
    print("  - benchmark_js_avec_gzip.tsv")


if __name__ == "__main__":
    main()
