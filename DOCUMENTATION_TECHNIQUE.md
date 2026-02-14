# Documentation Technique Complète du Serveur HTTP

> Documentation exhaustive du serveur HTTP asynchrone avec support PHP, MySQL et monitoring intégré

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du projet](#architecture-du-projet)
3. [Fichier principal : server.py](#fichier-principal-serverpy)
4. [Modules handlers](#modules-handlers)
5. [Modules utils](#modules-utils)
6. [Configuration et fichiers](#configuration-et-fichiers)
7. [Flux de données](#flux-de-données)
8. [Décisions d'architecture](#décisions-darchitecture)

---

## Vue d'ensemble

### Objectif du projet

Créer un serveur HTTP moderne en Python avec :
- **Asynchrone** : Gestion concurrente des requêtes via `asyncio`
- **PHP-CGI** : Exécution de scripts PHP comme Apache/Nginx
- **MySQL** : Accès base de données via API REST
- **Cache LRU** : Performance optimisée pour fichiers statiques
- **Monitoring** : Dashboard temps réel des performances
- **Production-ready** : Gestion sessions PHP, redirections, ETags

### Pourquoi ce projet ?

**Problème** : Les serveurs HTTP traditionnels (Apache, Nginx) sont complexes à configurer et comprendre.

**Solution** : Un serveur simple, lisible, éducatif mais fonctionnel, démontrant :
- Comment fonctionne HTTP en bas niveau
- Comment gérer PHP sans Apache
- Comment implémenter un cache efficace
- Comment monitorer les performances

---

## Architecture du projet

```
serveur-cURL/
├── server.py                    # Point d'entrée, orchestration HTTP
├── config.json                  # Configuration (port, root, redirections)
│
├── handlers/                    # Modules métier (logique applicative)
│   ├── api_sql.py              # API REST pour requêtes SQL
│   ├── cache.py                # Cache LRU pour fichiers statiques
│   ├── database.py             # Connecteur MySQL (aiomysql)
│   ├── directory_listing.py    # Génération listings de répertoires
│   ├── monitoring.py           # Collecte métriques de performance
│   ├── monitoring_widget.py    # Widget JavaScript injecté dans HTML
│   ├── php_cgi.py              # Exécution PHP via CGI
│   ├── redirect.py             # Gestion redirections 301/302
│   └── static.py               # Serveur fichiers statiques (HTML, CSS, JS)
│
├── utils/                       # Utilitaires génériques
│   ├── http_parser.py          # Parser requêtes/réponses HTTP
│   └── mime_types.py           # Détection types MIME
│
└── www/                         # Document root (fichiers servis)
    ├── index.html              # Page d'accueil
    ├── static/                 # Assets (CSS, JS, images)
    └── api/test_prog_sys/      # Application PHP CRUD exemple
```

### Principe de séparation

**Pourquoi cette structure ?**

1. **server.py** = Chef d'orchestre
   - Écoute les connexions TCP
   - Parse les requêtes HTTP
   - Route vers le bon handler
   - N'implémente AUCUNE logique métier

2. **handlers/** = Modules spécialisés
   - Chaque fichier = une responsabilité unique
   - Réutilisables et testables indépendamment
   - Ex : `php_cgi.py` peut être utilisé dans un autre projet

3. **utils/** = Code générique
   - Fonctions sans dépendance au projet
   - Peuvent être extraites dans une librairie

**Avantage** : Modularité, maintenabilité, compréhension facilitée

---

## Fichier principal : server.py

### Responsabilités

1. **Initialisation** : Charger config, démarrer serveur TCP
2. **Réception** : Accepter connexions, lire requêtes HTTP
3. **Routage** : Décider quel handler appeler selon l'URL
4. **Réponse** : Envoyer la réponse HTTP au client

### Fonction `main()` - Point d'entrée

```python
async def main():
    global CONFIG
    CONFIG = load_config()  # Charge config.json
    
    host = CONFIG['host']   # 0.0.0.0 (écoute toutes interfaces)
    port = CONFIG['port']   # 4610
    
    # Initialiser MySQL (optionnel)
    await database.init_db()
    
    # Démarrer serveur TCP
    server = await asyncio.start_server(handle_request, host, port)
    
    # Boucle infinie, attend connexions
    await server.serve_forever()
```

**Pourquoi `asyncio` ?**
- **Concurrent** : Gère 1000+ connexions simultanées avec 1 thread
- **Non-bloquant** : Pendant lecture réseau, Python traite autre chose
- **Moderne** : Standard Python pour I/O asynchrone

**Pourquoi `start_server()` ?**
- Abstraction haut niveau de `socket.socket()`
- Gère accept() et création StreamReader/Writer automatiquement

---

### Fonction `handle_request()` - Cœur du serveur

**Signature**
```python
async def handle_request(reader: asyncio.StreamReader, 
                        writer: asyncio.StreamWriter) -> None
```

**Paramètres**
- `reader` : Flux entrant (requête HTTP du client)
- `writer` : Flux sortant (réponse HTTP vers client)

**Pourquoi async ?**
- `await reader.read()` ne bloque pas le thread pendant l'attente réseau
- Permet de gérer d'autres connexions en parallèle

**Logique détaillée**

#### Étape 1 : Lire les headers HTTP

```python
data = b''
while not data.endswith(b'\r\n\r\n'):  # Fin headers = double CRLF
    chunk = await reader.read(1024)
    if not chunk:
        break
    data += chunk
    if len(data) > 8192:  # Protection contre requêtes géantes
        return build_http_response(400, "Bad Request")
```

**Pourquoi cette boucle ?**
- HTTP = protocole texte délimité par `\r\n\r\n`
- Les headers peuvent arriver en plusieurs paquets TCP
- Lecture incrémentale jusqu'au marqueur de fin

**Pourquoi limite 8192 octets ?**
- Sécurité : empêche attaques mémoire (headers infinis)
- 8KB = largement suffisant pour headers normaux

#### Étape 2 : Parser la requête

```python
method, path, version, headers, _ = parse_http_request(headers_part)
```

**Extraction**
- `method` : GET, POST, PUT, DELETE...
- `path` : `/index.html?user=john`
- `headers` : `{'host': 'localhost', 'user-agent': '...'}`

#### Étape 3 : Lire le body (POST/PUT)

```python
content_length = headers.get('content-length')
if content_length:
    content_length = int(content_length)
    while len(body) < content_length:
        chunk = await reader.read(min(4096, content_length - len(body)))
        body += chunk
```

**Pourquoi après les headers ?**
- Le client envoie : `Headers\r\n\r\nBody`
- On lit d'abord headers pour connaître la taille du body (`Content-Length`)

**Pourquoi `min(4096, remaining)` ?**
- Optimisation : lire par blocs de 4KB (taille standard buffer TCP)
- Ne pas lire plus que nécessaire

#### Étape 4 : Routage - Décision du traitement

```python
# 1. Monitoring
if path_only == '/_monitor':
    return generate_monitoring_dashboard()

# 2. API SQL
if path_only == '/api/sql':
    return handle_api_sql(method, body)

# 3. Redirections
if redirect := get_redirect_location(path_only):
    return build_redirect_response(redirect)

# 4. Fichiers PHP
if file_path.endswith('.php'):
    return execute_php_cgi(file_path, method, body)

# 5. Fichiers statiques
return handle_static_file(file_path)
```

**Ordre d'importance**
1. **Routes spéciales** (`/_monitor`, `/api/sql`) : Toujours prioritaires
2. **Redirections** : Avant résolution fichiers (SEO)
3. **PHP** : Scripts dynamiques
4. **Statique** : Fallback par défaut

**Pourquoi cet ordre ?**
- Performance : Routes spéciales = vérification rapide (string match)
- Logique : Redirection avant 404 (l'ancienne URL peut ne plus exister)

#### Étape 5 : Gestion des répertoires

```python
if os.path.isdir(file_path):
    # Chercher index.html, index.php...
    for index_file in CONFIG.get('index_files', ['index.html']):
        index_path = os.path.join(file_path, index_file)
        if os.path.isfile(index_path):
            file_path = index_path
            break
    else:
        # Pas d'index => listing de répertoire
        return generate_directory_listing(file_path)
```

**Comportement Apache-like**
- `/blog/` → Cherche `/blog/index.html`, `/blog/index.php`
- Si aucun : Génère listing HTML automatique

**Pourquoi un tableau `index_files` ?**
- Flexibilité : PHP en priorité ? `['index.php', 'index.html']`
- Configuration sans modifier le code

---

### Fonctions utilitaires

#### `compute_etag(content)`

**Rôle** : Générer un identifiant unique du contenu

```python
return hashlib.md5(content).hexdigest()
```

**Utilité**
- Cache navigateur : `ETag: "a1b2c3d4"` → Client renvoie `If-None-Match: "a1b2c3d4"`
- Si identique → `304 Not Modified` (économise bande passante)

**Pourquoi MD5 ?**
- Rapide (important pour chaque requête)
- Collision improbable pour fichiers web
- Pas de sécurité ici (juste identification)

#### `resolve_path(path, document_root)`

**Rôle** : Convertir URL en chemin système sécurisé

```python
# Exemples
resolve_path('/index.html', '/var/www') → '/var/www/index.html'
resolve_path('/../etc/passwd', '/var/www') → '' (rejeté)
```

**Sécurité**
```python
if '..' in path:
    return ''  # Empêche remontée de répertoires
    
full_path = os.path.join(document_root, path.lstrip('/'))

# Vérifier que le chemin final est dans document_root
if not os.path.abspath(full_path).startswith(os.path.abspath(document_root)):
    return ''
```

**Pourquoi cette vérification ?**
- **Attaque path traversal** : `/../../etc/passwd`
- Sans vérification → Accès fichiers système !
- `os.path.abspath()` : Résout `.` et `..` puis vérifie confinement

---

## Modules handlers

### handlers/database.py - Connecteur MySQL

#### Configuration

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',      # XAMPP par défaut
    'db': 'serveur_db',
    'charset': 'utf8mb4'
}
```

**Pourquoi `utf8mb4` ?**
- Support emojis et caractères Unicode complets
- `utf8` MySQL = seulement 3 octets (incomplet)

#### `init_db()` - Initialisation du pool

```python
pool = await aiomysql.create_pool(
    minsize=1,   # 1 connexion minimum (toujours ouverte)
    maxsize=10   # 10 connexions maximum (pic de charge)
)
```

**Pourquoi un pool ?**
- **Performance** : Créer/fermer connexions = lent (handshake TCP/MySQL)
- **Réutilisation** : Connexions partagées entre requêtes
- **Limite** : Évite saturation MySQL (max_connections)

**minsize=1 ?**
- Au moins 1 connexion chaude → Première requête instantanée

**maxsize=10 ?**
- Serveur web typique : 10-50 connexions DB suffisent
- Au-delà : Goulet d'étranglement est la base, pas le serveur

#### `execute_query()` - Exécution SQL

```python
async def execute_query(sql: str, params: tuple = None) -> Dict:
    # Conversion ? → %s (aiomysql utilise format Python)
    sql = sql.replace('?', '%s')
    
    async with pool.acquire() as conn:
        await conn.autocommit(True)  # Pas de transactions explicites
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, params)
            
            if sql.strip().upper().startswith('SELECT'):
                rows = await cursor.fetchall()
                return {'rows': rows, 'rowcount': len(rows)}
            else:
                return {'rowcount': cursor.rowcount, 'lastrowid': cursor.lastrowid}
```

**Paramètres**
- `sql` : Requête SQL avec placeholders (`?` ou `%s`)
- `params` : Valeurs à insérer (sécurité contre SQL injection)

**Conversion `?` → `%s`**
- Standard SQLite/Java : `SELECT * FROM users WHERE id = ?`
- Standard Python/MySQL : `SELECT * FROM users WHERE id = %s`
- Conversion = Compatibilité API

**Pourquoi `autocommit(True)` ?**
- Simplicité : Chaque requête = transaction immédiate
- Sans : Il faudrait `BEGIN`, `COMMIT` manuels
- API REST = Généralement requêtes isolées (pas de transactions multi-requêtes)

**Pourquoi `DictCursor` ?**
```python
# Cursor normal
row = (1, 'Alice', 'alice@example.com')

# DictCursor
row = {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
```
- Dictionnaires = Sérialisables en JSON directement
- Plus lisible dans l'API REST

**Gestion SELECT vs INSERT/UPDATE**
- SELECT → Retourne lignes (`fetchall()`)
- Autres → Retourne nombre lignes affectées et ID inséré

**Conversion datetime**
```python
for row in rows:
    for key, value in row.items():
        if hasattr(value, 'isoformat'):
            row[key] = str(value)
```
- MySQL `DATETIME` → Python `datetime.datetime`
- `datetime` non sérialisable en JSON
- Conversion en string ISO : `"2026-02-14T10:30:00"`

---

### handlers/api_sql.py - API REST SQL

#### Endpoint unique

```
POST /api/sql
Content-Type: application/json

{
    "sql": "SELECT * FROM users WHERE id = %s",
    "params": [1]
}
```

**Réponse**
```json
{
    "success": true,
    "result": {
        "rows": [{"id": 1, "name": "Alice"}],
        "rowcount": 1
    }
}
```

#### Fonction `handle_api_sql()`

```python
async def handle_api_sql(method, path, body, query_string):
    if method != 'POST':
        return (405, json.dumps({'error': 'Seul POST autorisé'}).encode(), 'application/json')
    
    data = json.loads(body.decode())
    sql = data.get('sql', '').strip()
    params = tuple(data.get('params', []))
    
    result = await db.execute_query(sql, params)
    
    return (200, json.dumps({'success': True, 'result': result}).encode(), 'application/json')
```

**Pourquoi POST uniquement ?**
- GET = Idempotent, pas d'effets de bord (standard REST)
- SQL peut modifier données (`INSERT`, `UPDATE`)
- POST = Méthode pour actions modifiant l'état

**Pourquoi JSON ?**
- Standard API REST
- Facile à parser côté client (JavaScript, Python, PHP...)
- Support arrays et objets complexes

**Sécurité**
- ⚠️ **AUCUNE** : N'importe qui peut exécuter `DROP TABLE users`
- **Pour démo uniquement** : Production = Authentification + Whitelist requêtes

**Pourquoi comme ça ?**
- **Simplification** : Évite ORM, autentification, permissions
- **Éducatif** : Montre fonctionnement API REST bas niveau
- **Flexibilité** : Client peut faire n'importe quelle requête (dev rapide)

---

### handlers/php_cgi.py - Exécution PHP

#### Principe CGI (Common Gateway Interface)

**Historique** : Standard 1993 pour exécuter scripts serveur (Perl, PHP...)

**Fonctionnement**
1. Serveur web reçoit requête vers `/script.php`
2. Lance processus `/usr/bin/php-cgi script.php`
3. Passe requête via variables d'environnement
4. Récupère réponse sur stdout
5. Renvoie au client

**Différence FastCGI**
- CGI : 1 processus par requête (lent)
- FastCGI : Processus persistent (rapide)
- Ici : CGI = Simplicité (suffisant pour démo)

#### Fonction `execute_php_cgi()`

```python
async def execute_php_cgi(script_path, method, query_string, headers, body, php_cgi_path):
    # 1. Construire environnement CGI
    env = build_cgi_env(script_path, method, query_string, headers, body)
    
    # 2. Lancer php-cgi
    process = await asyncio.create_subprocess_exec(
        php_cgi_path,
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )
    
    # 3. Envoyer body POST et lire réponse
    stdout, stderr = await process.communicate(input=body)
    
    # 4. Parser sortie CGI
    content, extra_headers = parse_cgi_output(stdout)
    
    return content, extra_headers
```

**Paramètres**
- `script_path` : `/path/to/script.php` (absolu)
- `method` : `POST`
- `query_string` : `user=john&age=25`
- `headers` : `{'content-type': 'application/x-www-form-urlencoded'}`
- `body` : `name=Alice&email=alice@example.com` (bytes)

**Pourquoi `asyncio.create_subprocess_exec()` ?**
- Version async de `subprocess.Popen()`
- `await process.communicate()` ne bloque pas event loop
- Serveur peut traiter autres requêtes pendant exécution PHP

**Pourquoi `stdin=PIPE` ?**
- Pour envoyer le body POST à PHP
- PHP lit `php://input` → données viennent de stdin

#### Fonction `build_cgi_env()` - Variables d'environnement

```python
env = {
    'REQUEST_METHOD': 'POST',
    'SCRIPT_FILENAME': '/var/www/script.php',
    'QUERY_STRING': 'user=john',
    'CONTENT_LENGTH': '42',
    'CONTENT_TYPE': 'application/x-www-form-urlencoded',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'REDIRECT_STATUS': '200',  # Spécifique PHP-CGI
    'HTTP_USER_AGENT': 'Mozilla/5.0...',
    'HTTP_COOKIE': 'PHPSESSID=abc123...'
}
```

**Variables clés**

| Variable | Valeur | Utilité PHP |
|----------|--------|-------------|
| `REQUEST_METHOD` | `POST` | `$_SERVER['REQUEST_METHOD']` |
| `QUERY_STRING` | `?user=john` | `$_GET['user']` |
| `CONTENT_LENGTH` | `42` | Taille `$_POST` |
| `HTTP_*` | Headers | `$_SERVER['HTTP_USER_AGENT']` |

**Pourquoi `REDIRECT_STATUS=200` ?**
- Bug historique PHP-CGI : Refuse de s'exécuter sans cette variable
- Sécurité contre exécution directe (sans serveur web)

**Conversion headers HTTP → CGI**
```python
# Header HTTP: User-Agent: Mozilla/5.0
# Variable CGI: HTTP_USER_AGENT=Mozilla/5.0

cgi_name = f"HTTP_{header_name.upper().replace('-', '_')}"
```

- Standard CGI : Prefixe `HTTP_` + Majuscules + `_` au lieu de `-`

#### Fonction `parse_cgi_output()` - Parser réponse PHP

**Format sortie CGI**
```
Status: 200 OK
Content-Type: text/html
Set-Cookie: session=abc123

<!DOCTYPE html>
<html>...
```

**Parsing**
```python
# Séparer headers et body
if '\r\n\r\n' in output:
    header_part, body = output.split('\r\n\r\n', 1)

# Parser headers
headers = {}
for line in header_part.split('\r\n'):
    if ': ' in line:
        key, value = line.split(': ', 1)
        headers[key.lower()] = value

return body.encode('utf-8'), headers
```

**Headers spéciaux**
- `Status: 302 Found` → Code HTTP (redirection)
- `Location: /other-page.php` → URL redirection
- `Set-Cookie: ...` → Session PHP

**Gestion redirections PHP**
```php
<?php
header('Location: /success.php');
exit();
?>
```

**Sortie CGI**
```
Status: 302 Found
Location: /success.php
Content-Type: text/html

(body vide)
```

**Détection serveur**
```python
if extra_headers and 'location' in extra_headers:
    # Construire réponse 302/303
    status_code = 303 if method == "POST" else 302
    response = f"HTTP/1.1 {status_code} See Other\r\n"
    response += f"Location: {location}\r\n"
    response += "Content-Length: 0\r\n\r\n"
```

**Pourquoi 303 après POST ?**
- Standard HTTP : POST → Redirect → GET
- 302 : Navigateur peut refaire le POST (double soumission formulaire)
- 303 : Force GET (comportement attendu)

**Headers anti-cache**
```python
headers_str += "Cache-Control: no-cache, no-store, must-revalidate\r\n"
headers_str += "Pragma: no-cache\r\n"
headers_str += "Expires: 0\r\n"
```
- Empêche navigateur de cacher la redirection
- Force nouvelle requête à chaque fois

---

### handlers/cache.py - Cache LRU

#### Principe LRU (Least Recently Used)

**Problème** : Servir 1000x le même fichier = Lire disque 1000x (lent)

**Solution** : Mettre en mémoire les fichiers récents

**Capacité limitée** : 200 fichiers max → Évincer les moins utilisés

**Algorithme**
```
Cache: [A, B, C, D, E]  (capacité = 5)

1. Accès C → C devient le plus récent
   Cache: [A, B, D, E, C]

2. Ajout F → A (plus ancien) est évincé
   Cache: [B, D, E, C, F]
```

#### Implémentation

```python
class LRUCache:
    def __init__(self, capacity=200):
        self.cache = OrderedDict()  # Dict qui garde l'ordre d'insertion
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
```

**Pourquoi `OrderedDict` ?**
- Dict normal : Ordre aléatoire (Python <3.7) ou insertion (3.7+)
- `OrderedDict` : Ordre garanti + `move_to_end()`

**Opération `get()`**
```python
def get(self, key):
    if key in self.cache:
        self.cache.move_to_end(key)  # Marquer comme récent
        self.hits += 1
        return self.cache[key]
    
    self.misses += 1
    return None
```

**Opération `put()`**
```python
def put(self, key, value):
    if key in self.cache:
        self.cache.move_to_end(key)
    else:
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)  # Évincer le plus ancien
    
    self.cache[key] = value
```

**`popitem(last=False)`**
- `last=True` (défaut) : Enlève le PLUS récent (LIFO - pile)
- `last=False` : Enlève le PLUS ancien (FIFO - LRU)

**Métriques**
```python
def get_stats(self):
    return {
        'size': len(self.cache),
        'capacity': self.capacity,
        'hits': self.hits,
        'misses': self.misses,
        'hit_rate': self.hits / (self.hits + self.misses) * 100
    }
```

**Interprétation**
- `hit_rate = 90%` → Excellent (90% requêtes servies depuis mémoire)
- `hit_rate = 10%` → Mauvais (cache trop petit ou contenu pas réutilisé)

**Pourquoi capacité=200 ?**
- Fichiers web = 10-100 KB moyenne
- 200 fichiers × 50 KB = 10 MB RAM (acceptable)
- Site typique = <200 fichiers actifs (HTML, CSS, JS, images communes)

---

### handlers/monitoring.py - Métriques de performance

#### Classe `PerformanceMonitor`

**Données collectées**

```python
class PerformanceMonitor:
    def __init__(self):
        self.total_requests = 0
        self.requests_by_method = {}    # {'GET': 500, 'POST': 50}
        self.requests_by_status = {}    # {200: 480, 404: 20}
        self.requests_by_path = {}      # {'/index.html': 100, ...}
        
        self.request_times = deque(maxlen=100)  # 100 dernières latences
        self.min_latency = float('inf')
        self.max_latency = 0
        self.total_latency = 0
        
        self.requests_history = deque(maxlen=100)  # 100 dernières requêtes
```

**Pourquoi `deque(maxlen=100)` ?**
- `deque` = Double-ended queue (file optimisée)
- `maxlen` = Taille fixe, évince automatiquement ancien
- Évite croissance mémoire infinie

#### Fonction `record_request()`

```python
def record_request(self, method, path, status_code, latency, client_ip):
    with self.lock:  # Thread-safe
        self.total_requests += 1
        self.requests_by_method[method] = self.requests_by_method.get(method, 0) + 1
        self.requests_by_status[status_code] = self.requests_by_status.get(status_code, 0) + 1
        
        latency_ms = latency * 1000
        self.request_times.append(latency_ms)
        self.min_latency = min(self.min_latency, latency_ms)
        self.max_latency = max(self.max_latency, latency_ms)
        
        self.requests_history.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'method': method,
            'path': path,
            'status': status_code,
            'latency': f"{latency_ms:.2f}ms",
            'ip': client_ip
        })
```

**Pourquoi `self.lock` ?**
- `asyncio` = Mono-thread MAIS requêtes concurrentes
- Opérations comme `+=` ne sont pas atomiques
- `threading.Lock()` = Exclusion mutuelle (1 seule task à la fois)

**Calculs statistiques**
```python
def get_stats(self):
    avg_latency = self.total_latency / len(self.request_times) if self.request_times else 0
    
    return {
        'total_requests': self.total_requests,
        'avg_latency': f"{avg_latency:.2f}ms",
        'min_latency': f"{self.min_latency:.2f}ms",
        'max_latency': f"{self.max_latency:.2f}ms",
        'uptime': time.time() - self.start_time,
        ...
    }
```

**Dashboard HTML**
- Endpoint `/_monitor` → Génère page HTML avec graphiques
- JavaScript fait polling `/_monitor/api` toutes les 2 secondes
- Affiche métriques temps réel (Chart.js)

---

### handlers/static.py - Fichiers statiques

#### Fonction `handle_static_file()`

```python
async def handle_static_file(file_path, if_none_match=None):
    # 1. Vérifier cache
    cached = static_cache.get(file_path)
    if cached:
        content, etag = cached
        # Valider ETag client
        if if_none_match == etag:
            return b'', {'ETag': etag}  # 304 Not Modified
        return content, {'ETag': etag, 'Content-Type': get_mime_type(file_path)}
    
    # 2. Lire fichier disque
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 3. Générer ETag et mettre en cache
    etag = compute_etag(content)
    static_cache.put(file_path, (content, etag))
    
    return content, {'ETag': etag, 'Content-Type': get_mime_type(file_path)}
```

**Flux de décision**
```
Requête /style.css
    ↓
Cache contient style.css ?
    ↓ Oui
Client envoie If-None-Match: "abc123" ?
    ↓ Oui, et correspond
Retour 304 Not Modified (0 octets envoyés)

Requête /image.png
    ↓
Cache contient image.png ?
    ↓ Non
Lire fichier disque
    ↓
Calculer ETag = "def456"
    ↓
Mettre en cache
    ↓
Retour 200 OK + contenu complet
```

**Optimisations**
- **Cache serveur** : Évite lectures disque répétées
- **ETag** : Évite envoi contenu si inchangé
- **Cache-Control** : `public, max-age=3600` → Cache navigateur 1h

**Pourquoi binaire (`rb`) ?**
- Images, PDF, vidéos = Fichiers binaires
- Mode texte (`r`) = Conversion encodage (peut corrompre)

---

## Modules utils

### utils/http_parser.py

#### Fonction `parse_http_request()`

```python
def parse_http_request(raw_data):
    # Parser ligne de requête
    lines = raw_data.decode().split('\r\n')
    request_line = lines[0]
    method, path, version = request_line.split(' ')
    
    # Parser headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    # Séparer path et query string
    if '?' in path:
        path, query_string = path.split('?', 1)
    else:
        query_string = ''
    
    return method, path, version, headers, query_string
```

**Exemple**
```
Entrée:
GET /search?q=python HTTP/1.1\r\n
Host: localhost\r\n
User-Agent: curl/7.0\r\n
\r\n

Sortie:
method = "GET"
path = "/search"
version = "HTTP/1.1"
headers = {'host': 'localhost', 'user-agent': 'curl/7.0'}
query_string = "q=python"
```

#### Fonction `build_http_response()`

```python
def build_http_response(status_code, body, extra_headers=None):
    status_text = {
        200: 'OK',
        301: 'Moved Permanently',
        302: 'Found',
        304: 'Not Modified',
        400: 'Bad Request',
        404: 'Not Found',
        500: 'Internal Server Error'
    }[status_code]
    
    response = f"HTTP/1.1 {status_code} {status_text}\r\n"
    response += "Content-Type: text/html; charset=utf-8\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    
    if extra_headers:
        for key, value in extra_headers.items():
            response += f"{key}: {value}\r\n"
    
    response += "\r\n"
    return response.encode() + body.encode()
```

**Pourquoi `\r\n` ?**
- Standard HTTP : CRLF (Carriage Return + Line Feed)
- Héritage Telnet (1970s)
- `\n` seul (Unix) = Non conforme

---

### utils/mime_types.py

```python
MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.pdf': 'application/pdf',
    ...
}

def get_mime_type(file_path):
    ext = os.path.splitext(file_path)[1]
    return MIME_TYPES.get(ext, 'application/octet-stream')
```

**Pourquoi important ?**
- Navigateur utilise `Content-Type` pour savoir comment traiter
- `text/html` → Render HTML
- `image/png` → Afficher image
- `application/octet-stream` → Télécharger

---

## Configuration et fichiers

### config.json

```json
{
    "host": "0.0.0.0",
    "port": 4610,
    "document_root": "./www",
    "index_files": ["index.html", "index.php"],
    "enable_php": true,
    "php_cgi_path": "/usr/bin/php-cgi",
    "redirects": {
        "/old-page": {
            "location": "/new-page",
            "permanent": true
        }
    }
}
```

**host = "0.0.0.0"**
- Écoute sur toutes interfaces réseau
- Accessible depuis : `localhost`, `127.0.0.1`, IP locale

**port = 4610**
- Port non privilégié (>1024, pas besoin root)
- Évite conflit avec services courants (80=HTTP, 8080=proxy)

**document_root = "./www"**
- Racine des fichiers servis
- Chemin relatif → Flexible

**index_files**
- Ordre de priorité pour fichiers index
- Utile pour sites PHP : `["index.php", "index.html"]`

**redirects**
- SEO : Anciennes URLs → Nouvelles
- `permanent=true` → 301 (moteurs de recherche mettent à jour)
- `permanent=false` → 302 (temporaire)

---

## Flux de données

### Requête GET simple

```
1. Client → Serveur : GET /index.html HTTP/1.1

2. handle_request()
   ↓
3. parse_http_request() → method="GET", path="/index.html"
   ↓
4. resolve_path() → /var/www/index.html
   ↓
5. handle_static_file()
   ↓
   Cache hit ? → Oui → content, etag
   ↓
6. Construire réponse HTTP
   ↓
7. Serveur → Client : HTTP/1.1 200 OK + contenu
```

### Requête POST PHP avec redirection

```
1. Client → Serveur : POST /form.php + body

2. handle_request()
   ↓
3. Lire body (Content-Length)
   ↓
4. execute_php_cgi()
   ↓
   4a. build_cgi_env() → Variables d'environnement
   ↓
   4b. Lancer processus php-cgi
   ↓
   4c. Envoyer body via stdin
   ↓
   4d. Lire stdout (réponse PHP)
   ↓
   4e. parse_cgi_output() → body, headers
   ↓
5. Détection header "Location" → Redirection
   ↓
6. Construire réponse 303 See Other
   ↓
7. Serveur → Client : HTTP/1.1 303 + Location: /success.php
   ↓
8. Navigateur suit automatiquement → GET /success.php
```

### Requête API SQL

```
1. Client → Serveur : POST /api/sql
   Body: {"sql": "SELECT * FROM users", "params": []}

2. handle_request()
   ↓
3. Routage : path == "/api/sql" → handle_api_sql()
   ↓
4. JSON.parse(body) → sql, params
   ↓
5. database.execute_query(sql, params)
   ↓
   5a. Acquérir connexion depuis pool
   ↓
   5b. cursor.execute(sql, params)
   ↓
   5c. fetchall() → rows
   ↓
6. Construire JSON : {"success": true, "result": {...}}
   ↓
7. Serveur → Client : HTTP/1.1 200 OK + JSON
```

---

## Décisions d'architecture

### Pourquoi asyncio et pas threads ?

**Threads**
```python
for each request:
    thread = Thread(target=handle_request)
    thread.start()
```
- **Problème** : 1000 requêtes = 1000 threads = Overhead mémoire/CPU
- Changements de contexte coûteux

**Asyncio**
```python
async for each request:
    await handle_request()
```
- **Avantage** : 1 thread, boucle événementielle
- Pendant I/O (réseau, disque), traite autre chose
- 10 000+ connexions simultanées possibles

**Quand threads > asyncio ?**
- Calculs CPU-intensifs (cryptographie, compression)
- Ici : I/O majoritaire (réseau, fichiers) → asyncio parfait

### Pourquoi PHP-CGI et pas mod_php ?

**mod_php** : PHP intégré dans le processus serveur (Apache)
- **Avantage** : Rapide (pas de processus externe)
- **Inconvénient** : Nécessite compiler serveur avec PHP

**PHP-CGI** : Processus externe
- **Avantage** : Indépendant du serveur, simple
- **Inconvénient** : Plus lent (fork processus)

**Choix CGI** : Simplicité et portabilité (juste installer php-cgi)

**Production** : FastCGI (processus persistent, meilleur des 2)

### Pourquoi cache global et pas par connexion ?

```python
# Global (choisi)
static_cache = LRUCache(capacity=200)

# Par connexion (rejeté)
async def handle_request():
    cache = LRUCache(capacity=200)
```

**Raison** : Partage entre toutes les requêtes
- Requête 1 met `/style.css` en cache
- Requête 2 réutilise immédiatement

**Par connexion** : Chaque client son propre cache = Inefficace

### Pourquoi monitoring toujours actif ?

**Alternative** : Activer monitoring seulement en dev
```python
if CONFIG['debug']:
    monitor.record_request(...)
```

**Choix actuel** : Toujours actif
- **Overhead** : ~0.1ms par requête (négligeable)
- **Bénéfice** : Dashboard toujours disponible (debug production)

**Production réelle** : Désactiver ou utiliser APM externe (New Relic, Datadog)

### Pourquoi MySQL et pas SQLite ?

**SQLite** : Base de données fichier (1 fichier .db)
- **Avantage** : Zéro configuration
- **Inconvénient** : Verrous fichier, 1 écriture à la fois

**MySQL** : Serveur base de données
- **Avantage** : Concurrent, scalable
- **Inconvénient** : Installation XAMPP nécessaire

**Choix MySQL** : Réaliste (production = toujours serveur DB)

### Pourquoi injection widget monitoring ?

```python
content = inject_monitoring_widget(content)
```

**Injecte** : Script JavaScript dans chaque page HTML

**Pourquoi ?**
- Dashboard accessible depuis n'importe quelle page
- Développeurs voient métriques en temps réel

**Désactivation** : Commenter ligne dans `server.py`

---

## Résumé des responsabilités

| Fichier | Rôle | Entrée | Sortie |
|---------|------|--------|--------|
| `server.py` | Orchestration HTTP | Requête TCP | Réponse HTTP |
| `handlers/database.py` | Accès MySQL | SQL + params | Résultats |
| `handlers/api_sql.py` | API REST SQL | JSON | JSON |
| `handlers/php_cgi.py` | Exécution PHP | Script + params | HTML |
| `handlers/cache.py` | Mémoire cache | Clé | Valeur ou None |
| `handlers/monitoring.py` | Métriques | Événement | Stats |
| `handlers/static.py` | Fichiers | Chemin | Contenu |
| `utils/http_parser.py` | Parser HTTP | Bytes | Objets Python |
| `utils/mime_types.py` | Types MIME | Extension | MIME type |

---

## Questions fréquentes

### Où sont gérées les sessions PHP ?

**Réponse** : Par PHP lui-même via `php-cgi`

1. Client envoie `Cookie: PHPSESSID=abc123`
2. Serveur passe cookie dans `HTTP_COOKIE` (variable CGI)
3. PHP lit `$_COOKIE['PHPSESSID']`
4. PHP charge session depuis `/tmp/sess_abc123`
5. PHP modifie session et enregistre

**Serveur HTTP** : Juste un passeur de cookies (transparent)

### Pourquoi les paramètres SQL utilisent-ils %s ?

**Code**
```python
sql = "SELECT * FROM users WHERE id = ?"
sql = sql.replace('?', '%s')  # Conversion
cursor.execute(sql, (user_id,))
```

**Raison** : Compatibilité drivers

| Driver | Placeholder |
|--------|-------------|
| SQLite (Python) | `?` |
| MySQL (Python) | `%s` |
| PostgreSQL (Python) | `%s` |
| MySQL (Java) | `?` |

**Choix** : Accepter `?` (plus universel) et convertir

### Comment ajouter authentification ?

**Middleware** : Fonction exécutée avant handlers

```python
def require_auth(headers):
    auth = headers.get('authorization')
    if not auth or not verify_token(auth):
        return build_http_response(401, "Unauthorized")
    return None  # OK

async def handle_request():
    # Avant routage
    if path == '/api/sql':
        error = require_auth(headers)
        if error:
            writer.write(error)
            return
    
    # Continuer normalement
```

**Où mettre ce code** : Dans `server.py`, avant le routage

---

## Conclusion

Ce serveur est un **exemple pédagogique** démontrant :
- Architecture modulaire propre
- Gestion asynchrone moderne
- Intégration technologies web (PHP, MySQL)
- Monitoring et observabilité

**Points forts**
- Code lisible et documenté
- Fonctionnalités complètes
- Extensible facilement

**Limitations**
- Sécurité minimale (pas d'authentification)
- Performance (CGI vs FastCGI)
- Pas de HTTPS

**Production** : Utilisez Nginx/Apache + PHP-FPM + Gunicorn/uvicorn

**Usage** : Apprentissage, prototypage, démonstrations techniques
