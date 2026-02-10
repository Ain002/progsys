"""
Widget de monitoring minimaliste à injecter dans les pages HTML
"""

def get_monitoring_widget() -> str:
    """Retourne le code HTML/JS du widget de monitoring à injecter"""
    
    return """
<!-- Widget de monitoring -->
<div id="perf-widget" style="position: fixed; bottom: 10px; right: 10px; background: rgba(0,0,0,0.85); color: white; padding: 10px 15px; border-radius: 8px; font-family: monospace; font-size: 11px; z-index: 10000; box-shadow: 0 4px 6px rgba(0,0,0,0.3); min-width: 200px; backdrop-filter: blur(10px); transition: all 0.3s;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
        <span style="font-weight: bold; color: #4CAF50;">📊 Perf</span>
        <div>
            <span id="perf-toggle" style="cursor: pointer; font-size: 14px; margin-right: 8px;">▼</span>
            <span id="perf-close" style="cursor: pointer; font-size: 14px; color: #ff5252;" title="Masquer (Ctrl+Shift+P pour afficher)">✕</span>
        </div>
    </div>
    <div id="perf-content">
        <div style="margin: 3px 0; display: flex; justify-content: space-between;">
            <span style="color: #aaa;">Req:</span>
            <span id="perf-requests" style="color: #4CAF50; font-weight: bold;">-</span>
        </div>
        <div style="margin: 3px 0; display: flex; justify-content: space-between;">
            <span style="color: #aaa;">Req/s:</span>
            <span id="perf-rps" style="color: #2196F3; font-weight: bold;">-</span>
        </div>
        <div style="margin: 3px 0; display: flex; justify-content: space-between;">
            <span style="color: #aaa;">Latence:</span>
            <span id="perf-latency" style="color: #FF9800; font-weight: bold;">-</span>
        </div>
        <div style="margin: 3px 0; display: flex; justify-content: space-between;">
            <span style="color: #aaa;">Cache:</span>
            <span id="perf-cache" style="color: #9C27B0; font-weight: bold;">-</span>
        </div>
        <div style="margin: 3px 0; display: flex; justify-content: space-between;">
            <span style="color: #aaa;">Uptime:</span>
            <span id="perf-uptime" style="color: #607D8B; font-weight: bold;">-</span>
        </div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); text-align: center;">
            <a href="/_monitor" target="_blank" style="color: #4CAF50; text-decoration: none; font-size: 10px;">📈 Dashboard complet</a>
        </div>
    </div>
</div>

<!-- Bouton réapparition discret -->
<div id="perf-show-btn" style="display: none; position: fixed; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; padding: 8px 12px; border-radius: 50%; font-size: 16px; z-index: 10000; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.3); backdrop-filter: blur(5px);" title="Afficher les stats (Ctrl+Shift+P)">
    📊
</div>

<script>
(function() {
    const widget = document.getElementById('perf-widget');
    const showBtn = document.getElementById('perf-show-btn');
    const content = document.getElementById('perf-content');
    const toggleBtn = document.getElementById('perf-toggle');
    const closeBtn = document.getElementById('perf-close');
    
    let collapsed = false;
    let hidden = false;
    
    // Charger l'état depuis localStorage
    const savedState = localStorage.getItem('perfWidgetState');
    if (savedState === 'hidden') {
        widget.style.display = 'none';
        showBtn.style.display = 'block';
        hidden = true;
    } else if (savedState === 'collapsed') {
        content.style.display = 'none';
        toggleBtn.textContent = '▲';
        collapsed = true;
    }
    
    // Toggle collapse
    toggleBtn.onclick = function(e) {
        e.stopPropagation();
        collapsed = !collapsed;
        
        if (collapsed) {
            content.style.display = 'none';
            toggleBtn.textContent = '▲';
            localStorage.setItem('perfWidgetState', 'collapsed');
        } else {
            content.style.display = 'block';
            toggleBtn.textContent = '▼';
            localStorage.setItem('perfWidgetState', 'visible');
        }
    };
    
    // Masquer le widget
    closeBtn.onclick = function(e) {
        e.stopPropagation();
        widget.style.display = 'none';
        showBtn.style.display = 'block';
        hidden = true;
        localStorage.setItem('perfWidgetState', 'hidden');
    };
    
    // Afficher le widget
    showBtn.onclick = function() {
        widget.style.display = 'block';
        showBtn.style.display = 'none';
        hidden = false;
        localStorage.setItem('perfWidgetState', 'visible');
    };
    
    // Raccourci clavier Ctrl+Shift+P
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'P') {
            e.preventDefault();
            if (hidden) {
                widget.style.display = 'block';
                showBtn.style.display = 'none';
                hidden = false;
                localStorage.setItem('perfWidgetState', 'visible');
            } else {
                widget.style.display = 'none';
                showBtn.style.display = 'block';
                hidden = true;
                localStorage.setItem('perfWidgetState', 'hidden');
            }
        }
    });
    
    // Fetch stats
    function updateStats() {
        if (hidden) return; // Ne pas fetch si masqué
        
        fetch('/_monitor/api')
            .then(res => res.json())
            .then(data => {
                document.getElementById('perf-requests').textContent = data.total_requests || '-';
                document.getElementById('perf-rps').textContent = (data.requests_per_second?.current || 0).toFixed(1);
                document.getElementById('perf-latency').textContent = (data.latency?.avg || 0).toFixed(1) + 'ms';
                document.getElementById('perf-cache').textContent = data.cache?.hit_rate || '-';
                document.getElementById('perf-uptime').textContent = data.uptime_str || '-';
            })
            .catch(err => {
                console.error('Erreur fetch stats:', err);
            });
    }
    
    // Update every 2 seconds
    updateStats();
    setInterval(updateStats, 2000);
})();
</script>
"""


def inject_monitoring_widget(html_content: bytes) -> bytes:
    """
    Injecte le widget de monitoring dans une page HTML
    
    Args:
        html_content: Contenu HTML en bytes
        
    Returns:
        HTML modifié avec le widget
    """
    try:
        html_str = html_content.decode('utf-8')
        
        # Chercher la balise </body>
        if '</body>' in html_str.lower():
            widget = get_monitoring_widget()
            html_str = html_str.replace('</body>', widget + '\n</body>')
            return html_str.encode('utf-8')
        
        # Si pas de </body>, ajouter à la fin
        widget = get_monitoring_widget()
        return (html_str + widget).encode('utf-8')
        
    except:
        # Si erreur de décodage, retourner tel quel
        return html_content
