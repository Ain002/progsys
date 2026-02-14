// Test JavaScript
function testJS() {
    const result = document.getElementById('js-result');
    result.innerHTML = '<span class="success" style="margin-left: 10px;">✓ JavaScript fonctionne!</span>';
}

// Test Cache
let cacheCount = 0;
async function testCache() {
    const info = document.getElementById('cache-info');
    const stats = document.getElementById('cache-stats');
    info.innerHTML = '<p class="loading">Test en cours...</p>';
    
    const start = Date.now();
    for (let i = 0; i < 20; i++) {
        await fetch('/index.html');
    }
    const duration = Date.now() - start;
    
    const response = await fetch('/_monitor/api');
    const data = await response.json();
    
    info.innerHTML = `<p class="success">✓ 20 requêtes en ${duration}ms</p>`;
    stats.innerHTML = `
        <div class="result-box">
            <h4>Stats Cache:</h4>
            <p>Hits: <strong>${data.cache.hits}</strong></p>
            <p>Misses: <strong>${data.cache.misses}</strong></p>
            <p>Hit Rate: <strong>${data.cache.hit_rate}</strong></p>
            <p>Taille: ${data.cache.size}/${data.cache.capacity}</p>
        </div>
    `;
}

// Test PHP
async function testPHP(type) {
    const resultId = type === 'simple' ? 'php-simple' : 'php-get';
    const result = document.getElementById(resultId);
    result.innerHTML = '<p class="loading">Exécution PHP...</p>';
    
    try {
        let url = type === 'simple' ? '/test.php' : '/test.php?nom=Alice&age=25';
        const response = await fetch(url);
        const text = await response.text();
        result.innerHTML = `<div class="result-box"><pre>${text}</pre></div>`;
    } catch (error) {
        result.innerHTML = `<p class="error">✗ Erreur: ${error.message}</p>`;
    }
}

// Formulaire POST
function showPostForm() {
    const form = document.getElementById('post-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

async function testPHPPost() {
    const result = document.getElementById('php-post');
    result.innerHTML = '<p class="loading">Envoi POST...</p>';
    
    try {
        const formData = new URLSearchParams();
        formData.append('nom', document.getElementById('nom').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('message', document.getElementById('message').value);
        
        const response = await fetch('/test.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        const text = await response.text();
        result.innerHTML = `<div class="result-box" style="border-color: #28a745;"><pre>${text}</pre></div>`;
    } catch (error) {
        result.innerHTML = `<p class="error">✗ Erreur: ${error.message}</p>`;
    }
}

// Test JSON
async function testJSON() {
    const result = document.getElementById('json-result');
    result.textContent = 'Chargement...';
    
    try {
        const response = await fetch('/api/test.php');
        const data = await response.json();
        result.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        result.textContent = `Erreur: ${error.message}`;
    }
}

// Test Stats
async function testStats() {
    const result = document.getElementById('stats-result');
    result.textContent = 'Chargement...';
    
    try {
        const response = await fetch('/_monitor/api');
        const data = await response.json();
        result.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        result.textContent = `Erreur: ${error.message}`;
    }
}

// Test Concurrence
async function testConcurrency() {
    const result = document.getElementById('concurrency-result');
    result.innerHTML = '<p class="loading">Test de 50 requêtes simultanées...</p>';
    
    const start = Date.now();
    const promises = [];
    
    for (let i = 0; i < 50; i++) {
        promises.push(fetch('/index.html'));
    }
    
    try {
        const responses = await Promise.all(promises);
        const duration = Date.now() - start;
        const allSuccess = responses.every(r => r.ok);
        
        if (allSuccess) {
            result.innerHTML = `
                <div class="result-box" style="border-color: #28a745;">
                    <p class="success">✓ 50 requêtes simultanées réussies</p>
                    <p>Temps: <strong>${duration}ms</strong></p>
                    <p>Débit: ~${Math.round(50000/duration)} req/s</p>
                </div>
            `;
        } else {
            result.innerHTML = `<p class="error">⚠ Certaines requêtes ont échoué</p>`;
        }
    } catch (error) {
        result.innerHTML = `<p class="error">✗ Erreur: ${error.message}</p>`;
    }
}

// Génération de trafic
async function generateTraffic(count) {
    const result = document.getElementById('traffic-result');
    result.innerHTML = `<p class="loading">Génération de ${count} requêtes...</p>`;
    
    const start = Date.now();
    const promises = [];
    
    for (let i = 0; i < count; i++) {
        promises.push(fetch('/index.html', { method: 'HEAD' }));
    }
    
    try {
        await Promise.all(promises);
        const duration = Date.now() - start;
        
        result.innerHTML = `
            <div class="result-box" style="border-color: #28a745;">
                <p class="success">✓ ${count} requêtes en ${duration}ms</p>
                <p>Débit: <strong>~${Math.round(count * 1000 / duration)} req/s</strong></p>
                <p>Consultez le widget et /_monitor pour voir les stats!</p>
            </div>
        `;
    } catch (error) {
        result.innerHTML = `<p class="error">✗ Erreur: ${error.message}</p>`;
    }
}

console.log('%c🚀 Serveur HTTP Python', 'font-size: 20px; color: #667eea; font-weight: bold;');
console.log('%cToutes les fonctions de test sont disponibles', 'color: #764ba2;');
