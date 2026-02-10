"""
Module de monitoring des performances du serveur
"""

import time
import threading
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime

class PerformanceMonitor:
    """Moniteur de performance du serveur HTTP"""
    
    def __init__(self, max_requests_history: int = 100):
        self.max_requests_history = max_requests_history
        self.start_time = time.time()
        
        # Compteurs
        self.total_requests = 0
        self.requests_by_method = {}
        self.requests_by_status = {}
        self.requests_by_path = {}
        
        # Latences
        self.request_times = deque(maxlen=max_requests_history)
        self.min_latency = float('inf')
        self.max_latency = 0
        self.total_latency = 0
        
        # Historique des requêtes
        self.requests_history = deque(maxlen=max_requests_history)
        
        # Cache stats (sera mis à jour depuis l'extérieur)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'size': 0,
            'capacity': 0
        }
        
        # Compteur de requêtes par seconde
        self.requests_per_second = deque(maxlen=60)  # 60 dernières secondes
        self.current_second_requests = 0
        self.last_second_timestamp = int(time.time())
        
        # Thread-safe lock
        self.lock = threading.Lock()
    
    def record_request(self, method: str, path: str, status_code: int, 
                      latency: float, client_ip: str):
        """
        Enregistre une requête
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            path: Chemin demandé
            status_code: Code de statut HTTP
            latency: Temps de réponse en secondes
            client_ip: IP du client
        """
        with self.lock:
            # Compteurs globaux
            self.total_requests += 1
            
            # Par méthode
            self.requests_by_method[method] = self.requests_by_method.get(method, 0) + 1
            
            # Par status
            self.requests_by_status[status_code] = self.requests_by_status.get(status_code, 0) + 1
            
            # Par path
            self.requests_by_path[path] = self.requests_by_path.get(path, 0) + 1
            
            # Latences
            latency_ms = latency * 1000
            self.request_times.append(latency_ms)
            self.total_latency += latency_ms
            self.min_latency = min(self.min_latency, latency_ms)
            self.max_latency = max(self.max_latency, latency_ms)
            
            # Historique
            self.requests_history.append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'method': method,
                'path': path,
                'status': status_code,
                'latency': f"{latency_ms:.2f}ms",
                'ip': client_ip
            })
            
            # Requests per second
            current_second = int(time.time())
            if current_second != self.last_second_timestamp:
                self.requests_per_second.append(self.current_second_requests)
                self.current_second_requests = 1
                self.last_second_timestamp = current_second
            else:
                self.current_second_requests += 1
    
    def update_cache_stats(self, cache_stats: Dict):
        """Met à jour les stats du cache"""
        with self.lock:
            self.cache_stats = cache_stats
    
    def get_stats(self) -> Dict:
        """Retourne toutes les statistiques"""
        with self.lock:
            uptime = time.time() - self.start_time
            
            # Calculer la latence moyenne
            avg_latency = (self.total_latency / len(self.request_times)) if self.request_times else 0
            
            # Req/sec moyen
            avg_rps = self.total_requests / uptime if uptime > 0 else 0
            current_rps = sum(self.requests_per_second) / len(self.requests_per_second) if self.requests_per_second else 0
            
            # Top 10 paths
            top_paths = sorted(self.requests_by_path.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'uptime': int(uptime),
                'uptime_str': self._format_uptime(uptime),
                'total_requests': self.total_requests,
                'requests_per_second': {
                    'current': round(current_rps, 2),
                    'average': round(avg_rps, 2)
                },
                'latency': {
                    'min': round(self.min_latency, 2) if self.min_latency != float('inf') else 0,
                    'max': round(self.max_latency, 2),
                    'avg': round(avg_latency, 2),
                    'recent': [round(t, 2) for t in list(self.request_times)[-20:]]
                },
                'methods': dict(self.requests_by_method),
                'status_codes': dict(self.requests_by_status),
                'top_paths': [{'path': p, 'count': c} for p, c in top_paths],
                'cache': {
                    'hits': self.cache_stats.get('hits', 0),
                    'misses': self.cache_stats.get('misses', 0),
                    'hit_rate': self._calculate_hit_rate(),
                    'size': self.cache_stats.get('size', 0),
                    'capacity': self.cache_stats.get('capacity', 0)
                },
                'recent_requests': list(self.requests_history)[-20:]
            }
    
    def _calculate_hit_rate(self) -> str:
        """Calcule le taux de cache hits"""
        hits = self.cache_stats.get('hits', 0)
        misses = self.cache_stats.get('misses', 0)
        total = hits + misses
        if total == 0:
            return "0%"
        return f"{(hits / total * 100):.1f}%"
    
    def _format_uptime(self, seconds: float) -> str:
        """Formate l'uptime en format lisible"""
        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if days > 0:
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def reset(self):
        """Réinitialise toutes les statistiques"""
        with self.lock:
            self.start_time = time.time()
            self.total_requests = 0
            self.requests_by_method.clear()
            self.requests_by_status.clear()
            self.requests_by_path.clear()
            self.request_times.clear()
            self.min_latency = float('inf')
            self.max_latency = 0
            self.total_latency = 0
            self.requests_history.clear()
            self.requests_per_second.clear()
            self.current_second_requests = 0


# Instance globale
monitor = PerformanceMonitor()


def generate_monitoring_dashboard(stats: Dict) -> bytes:
    """Génère le HTML du dashboard de monitoring"""
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Monitoring Serveur HTTP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{
            color: #666;
            font-weight: 500;
        }}
        .metric-value {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}
        .big-number {{
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}
        .status-ok {{ color: #27ae60; }}
        .status-error {{ color: #e74c3c; }}
        .status-redirect {{ color: #f39c12; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }}
        .refresh-info {{
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .chart {{
            height: 100px;
            display: flex;
            align-items: flex-end;
            gap: 2px;
            margin-top: 15px;
        }}
        .bar {{
            flex: 1;
            background: linear-gradient(to top, #667eea, #764ba2);
            min-height: 2px;
            border-radius: 2px 2px 0 0;
            transition: height 0.3s;
        }}
        .progress-bar {{
            background: #f0f0f0;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            background: linear-gradient(to right, #667eea, #764ba2);
            height: 100%;
            transition: width 0.3s;
        }}
    </style>
    <script>
        // Auto-refresh toutes les 2 secondes
        setTimeout(function() {{
            location.reload();
        }}, 2000);
    </script>
</head>
<body>
    <div class="container">
        <h1>📊 Monitoring Serveur HTTP</h1>
        
        <div class="grid">
            <!-- Stats globales -->
            <div class="card">
                <h2>📈 Vue d'ensemble</h2>
                <div class="big-number">{stats['total_requests']}</div>
                <p style="text-align: center; color: #666; margin-bottom: 20px;">Requêtes totales</p>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">{stats['uptime_str']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Req/sec (actuel)</span>
                    <span class="metric-value">{stats['requests_per_second']['current']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Req/sec (moyen)</span>
                    <span class="metric-value">{stats['requests_per_second']['average']}</span>
                </div>
            </div>
            
            <!-- Latence -->
            <div class="card">
                <h2>⚡ Latence</h2>
                <div class="metric">
                    <span class="metric-label">Minimum</span>
                    <span class="metric-value">{stats['latency']['min']} ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Maximum</span>
                    <span class="metric-value">{stats['latency']['max']} ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Moyenne</span>
                    <span class="metric-value">{stats['latency']['avg']} ms</span>
                </div>
                <div class="chart">
                    {''.join(f'<div class="bar" style="height: {min(t/stats["latency"]["max"]*100 if stats["latency"]["max"] > 0 else 0, 100)}%;"></div>' for t in stats['latency']['recent'][-20:])}
                </div>
            </div>
            
            <!-- Cache -->
            <div class="card">
                <h2>💾 Cache</h2>
                <div class="metric">
                    <span class="metric-label">Hit Rate</span>
                    <span class="metric-value">{stats['cache']['hit_rate']}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {stats['cache']['hit_rate'].rstrip('%')}%;"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Hits</span>
                    <span class="metric-value status-ok">{stats['cache']['hits']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Misses</span>
                    <span class="metric-value status-error">{stats['cache']['misses']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Taille cache</span>
                    <span class="metric-value">{stats['cache']['size']} / {stats['cache']['capacity']}</span>
                </div>
            </div>
            
            <!-- Méthodes HTTP -->
            <div class="card">
                <h2>🔧 Méthodes HTTP</h2>
                {''.join(f'<div class="metric"><span class="metric-label">{method}</span><span class="metric-value">{count}</span></div>' for method, count in stats['methods'].items())}
            </div>
            
            <!-- Codes de statut -->
            <div class="card">
                <h2>📊 Codes de statut</h2>
                {''.join(f'<div class="metric"><span class="metric-label {self._get_status_class(code)}">{code}</span><span class="metric-value">{count}</span></div>' for code, count in sorted(stats['status_codes'].items()))}
            </div>
            
            <!-- Top paths -->
            <div class="card">
                <h2>🔝 Top Chemins</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Chemin</th>
                            <th style="text-align: right;">Requêtes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'<tr><td style="font-family: monospace; font-size: 0.85em;">{item["path"][:50]}</td><td style="text-align: right; font-weight: bold;">{item["count"]}</td></tr>' for item in stats['top_paths'][:10])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Requêtes récentes -->
        <div class="card">
            <h2>📝 Requêtes récentes</h2>
            <table>
                <thead>
                    <tr>
                        <th>Heure</th>
                        <th>Méthode</th>
                        <th>Chemin</th>
                        <th>Status</th>
                        <th>Latence</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'<tr><td>{req["timestamp"]}</td><td><strong>{req["method"]}</strong></td><td style="font-family: monospace; font-size: 0.85em;">{req["path"][:40]}</td><td class="{self._get_status_class(req["status"])}">{req["status"]}</td><td>{req["latency"]}</td><td style="font-family: monospace; font-size: 0.85em;">{req["ip"]}</td></tr>' for req in reversed(stats['recent_requests']))}
                </tbody>
            </table>
        </div>
        
        <div class="refresh-info">
            🔄 Rafraîchissement automatique toutes les 2 secondes
        </div>
    </div>
</body>
</html>"""
    
    return html.encode('utf-8')


def _get_status_class(code: int) -> str:
    """Retourne la classe CSS selon le code de statut"""
    if 200 <= code < 300:
        return 'status-ok'
    elif 300 <= code < 400:
        return 'status-redirect'
    else:
        return 'status-error'
