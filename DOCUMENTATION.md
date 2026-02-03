# Documentation - Serveur HTTP avec Support PHP

## 📋 Vue d'ensemble du projet

Création d'un **serveur HTTP complet** en Python pur, similaire à Apache, capable de :
- Gérer plusieurs connexions simultanées
- Servir des fichiers statiques (HTML, CSS, JS, images)
- Exécuter des scripts PHP via CGI
- Retourner du JSON, HTML, et autres types de contenu
- Gérer les redirections HTTP (301, 302)
- Implémenter un système de cache
- Gérer un fichier de configuration pour les routes

---

## 🏗️ Architecture

### Choix technologique : asyncio vs threading vs multiprocessing

| Solution | Avantages | Inconvénients | Recommandation |
|----------|-----------|---------------|----------------|
| **asyncio** | - Très léger (pas de threads)<br>- Excellent pour I/O (réseau, fichiers)<br>- Code moderne et élégant<br>- Supporte des milliers de connexions | - Complexité avec subprocess PHP<br>- Nécessite des bibliothèques async | ⭐ **RECOMMANDÉ** pour votre cas |
| **threading** | - Simple à comprendre<br>- Bon pour I/O bloquant<br>- Facile d'intégrer subprocess | - Limite ~500-1000 threads<br>- GIL Python (peu performant)<br>- Gestion mémoire plus lourde | ✓ Alternative solide |
| **multiprocessing** | - Vrai parallélisme CPU<br>- Contourne le GIL | - Très lourd en mémoire<br>- Overkill pour un serveur web | ✗ Pas adapté |

### 🎯 Choix recommandé : **asyncio**

**Pourquoi asyncio ?**
- Parfait pour gérer des milliers de connexions HTTP légères
- I/O non-bloquant natif
- Peut utiliser `asyncio.create_subprocess_exec()` pour PHP-CGI
- Code moderne et maintenable

**Structure avec asyncio :**
```python
import asyncio

async def handle_client(reader, writer):
    # Lit la requête HTTP
    # Traite (fichier statique ou PHP)
    # Envoie la réponse
    pass

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 4610)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

---

## 📂 Structure du projet (cible)

```
serveur-cURL/
├── DOCUMENTATION.md          # Ce fichier
├── README.md                 # Description courte du projet
├── server.py                 # Serveur HTTP principal (asyncio)
├── config.json               # Configuration (ports, routes, redirections)
├── handlers/
│   ├── __init__.py
│   ├── static.py            # Gestion fichiers statiques
│   ├── php_cgi.py           # Exécution PHP via CGI
│   ├── redirect.py          # Gestion redirections HTTP
│   └── cache.py             # Système de cache
├── utils/
│   ├── __init__.py
│   ├── http_parser.py       # Parser requêtes/réponses HTTP
│   └── mime_types.py        # Détection types MIME
├── www/                      # Racine web (fichiers servis)
│   ├── index.html
│   ├── index.php
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── api/
│       └── data.json
└── tests/
    ├── test_server.py
    ├── test_php.py
    └── test_cache.py
```

---

## 🔧 Concepts techniques à maîtriser

### 1. Le protocole HTTP

#### Requête HTTP
```
GET /index.php?user=john HTTP/1.1
Host: localhost:4610
User-Agent: Mozilla/5.0
Accept: text/html
Connection: keep-alive

[Body optionnel pour POST]
```

**Composants :**
- **Ligne de requête** : `METHOD PATH VERSION`
- **Headers** : Paires `Key: Value`
- **Ligne vide** : `\r\n\r\n`
- **Body** : Données POST/PUT

#### Réponse HTTP
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Cache-Control: max-age=3600

<html>...</html>
```

**Codes de statut importants :**
- `200 OK` - Succès
- `301 Moved Permanently` - Redirection permanente
- `302 Found` - Redirection temporaire
- `304 Not Modified` - Utiliser le cache
- `404 Not Found` - Ressource introuvable
- `500 Internal Server Error` - Erreur serveur

### 2. CGI (Common Gateway Interface)

**Principe :**
1. Le serveur reçoit une requête pour un fichier `.php`
2. Il lance `php-cgi` avec les variables d'environnement
3. PHP exécute le script et génère du HTML
4. Le serveur retourne le HTML au client

**Variables d'environnement CGI :**
```python
env = {
    'REQUEST_METHOD': 'GET',
    'QUERY_STRING': 'user=john&age=25',
    'CONTENT_TYPE': 'application/x-www-form-urlencoded',
    'CONTENT_LENGTH': '128',
    'SCRIPT_FILENAME': '/path/to/script.php',
    'SCRIPT_NAME': '/index.php',
    'PATH_INFO': '/extra/path',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '4610',
    'HTTP_HOST': 'localhost:4610',
    'HTTP_USER_AGENT': 'Mozilla/5.0',
    'HTTP_ACCEPT': 'text/html',
}
```

**Exécution avec asyncio :**
```python
process = await asyncio.create_subprocess_exec(
    'php-cgi', script_path,
    env=env,
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
stdout, stderr = await process.communicate(input=post_data)
```

### 3. Types MIME

**Associer extensions → Content-Type :**
```python
MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
}
```

### 4. Système de cache

**Stratégies de cache :**

#### Cache mémoire (LRU - Least Recently Used)
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity=100):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)  # Plus récent
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Retire le plus ancien
```

#### Headers de cache HTTP
```python
# Cache pour 1 heure
'Cache-Control': 'public, max-age=3600'

# Validation avec ETag
'ETag': '"hash-du-fichier"'
'If-None-Match': '"hash-du-fichier"'  # Client envoie
# → Serveur répond 304 Not Modified si identique
```

### 5. Redirections HTTP

```python
def redirect(location, permanent=False):
    code = 301 if permanent else 302
    status = "Moved Permanently" if permanent else "Found"
    
    response = (
        f"HTTP/1.1 {code} {status}\r\n"
        f"Location: {location}\r\n"
        f"Content-Length: 0\r\n"
        f"\r\n"
    )
    return response.encode()
```

**Cas d'usage :**
- `301` : `/old-page` → `/new-page` (permanent, SEO)
- `302` : `/login` → `/dashboard` (temporaire)
- `307` : Même chose mais préserve la méthode POST

---

## 📋 TODO LIST - Projet 1 mois

### ✅ Semaine 1 : Fondations (7 jours)

#### Jour 1-2 : Structure et parsing HTTP
- [ok] Créer la structure de dossiers du projet
- [ ] Implémenter `http_parser.py` :
  - [ ] Parser une requête HTTP complète
  - [ ] Parser les headers
  - [ ] Extraire méthode, path, query string
  - [ ] Gérer le body (POST)
- [ ] Implémenter `mime_types.py` :
  - [ ] Dictionnaire des types MIME
  - [ ] Fonction pour détecter le type depuis l'extension
- [ ] Tests unitaires pour le parser

#### Jour 3-4 : Serveur de base avec asyncio
- [ ] Créer `server.py` avec asyncio
- [ ] Implémenter la boucle principale :
  - [ ] `asyncio.start_server()`
  - [ ] Handler de connexion basique
  - [ ] Lecture requête HTTP complète
  - [ ] Envoi réponse simple (200 OK + texte)
- [ ] Tester avec curl : `curl http://localhost:4610/`
- [ ] Tester avec navigateur

#### Jour 5 : Fichiers statiques
- [ ] Créer le dossier `www/` avec des fichiers tests :
  - [ ] `index.html`
  - [ ] `style.css`
  - [ ] `script.js`
  - [ ] Une image PNG
- [ ] Implémenter `handlers/static.py` :
  - [ ] Lire un fichier depuis le disque
  - [ ] Détecter le type MIME
  - [ ] Gérer erreur 404 si fichier introuvable
  - [ ] Envoyer la réponse avec le bon Content-Type
- [ ] Tester dans le navigateur

#### Jour 6-7 : Configuration et routes
- [ ] Créer `config.json` :
  ```json
  {
    "host": "127.0.0.1",
    "port": 4610,
    "document_root": "./www",
    "index_files": ["index.html", "index.php"],
    "enable_php": true,
    "php_cgi_path": "/usr/bin/php-cgi",
    "cache_enabled": true,
    "cache_max_size": 100,
    "redirects": {
      "/old": "/new",
      "/admin": "/login"
    }
  }
  ```
- [ ] Charger et parser la config au démarrage
- [ ] Implémenter le système de routing basique

---

### ✅ Semaine 2 : Exécution PHP (7 jours)

#### Jour 8-9 : CGI basique
- [ ] Vérifier que `php-cgi` est installé : `which php-cgi`
- [ ] Créer un script PHP test `www/test.php` :
  ```php
  <?php
  echo "Hello from PHP!\n";
  echo "Query: " . $_SERVER['QUERY_STRING'];
  ?>
  ```
- [ ] Implémenter `handlers/php_cgi.py` :
  - [ ] Construire les variables d'environnement CGI
  - [ ] Lancer `php-cgi` avec `asyncio.create_subprocess_exec()`
  - [ ] Capturer stdout (réponse PHP)
  - [ ] Parser la sortie (headers + body)

#### Jour 10-11 : Gestion GET/POST
- [ ] Implémenter GET avec query string :
  - [ ] Parser `?param1=val1&param2=val2`
  - [ ] Passer dans `QUERY_STRING`
  - [ ] Tester avec `www/get.php` qui affiche `$_GET`
- [ ] Implémenter POST :
  - [ ] Lire le body de la requête
  - [ ] Passer dans stdin de php-cgi
  - [ ] Tester avec formulaire HTML

#### Jour 12-13 : JSON et API REST
- [ ] Créer `www/api/users.php` qui retourne du JSON :
  ```php
  <?php
  header('Content-Type: application/json');
  echo json_encode(['users' => ['Alice', 'Bob']]);
  ?>
  ```
- [ ] Tester avec curl : `curl http://localhost:4610/api/users.php`
- [ ] Créer des endpoints CRUD basiques
- [ ] Gérer les méthodes PUT, DELETE

#### Jour 14 : Gestion d'erreurs PHP
- [ ] Capturer stderr de php-cgi
- [ ] Logger les erreurs PHP
- [ ] Retourner 500 Internal Server Error si PHP crash
- [ ] Tester avec un script PHP qui génère une erreur

---
 
### ✅ Semaine 3 : Cache et optimisations (7 jours)

#### Jour 15-16 : Cache mémoire LRU
- [ ] Implémenter `handlers/cache.py` :
  - [ ] Classe `LRUCache` avec OrderedDict
  - [ ] Méthodes `get()` et `put()`
  - [ ] Éviction automatique si plein
- [ ] Intégrer dans le serveur :
  - [ ] Mettre en cache les fichiers statiques
  - [ ] Clé = chemin du fichier
  - [ ] Valeur = (contenu, mime_type, timestamp)
- [ ] Tests de performance

#### Jour 17-18 : Headers de cache HTTP
- [ ] Implémenter `Cache-Control` :
  - [ ] Fichiers statiques : `max-age=3600` (1h)
  - [ ] PHP : `no-cache` (pas de cache)
- [ ] Implémenter `ETag` :
  - [ ] Calculer hash MD5 du fichier
  - [ ] Envoyer dans header `ETag: "hash"`
  - [ ] Gérer `If-None-Match` du client
  - [ ] Retourner 304 Not Modified si identique

#### Jour 19-20 : Invalidation du cache
- [ ] Détecter si un fichier a changé (mtime)
- [ ] Invalider le cache si modifié
- [ ] Ajouter un endpoint admin pour vider le cache
- [ ] Logger les hits/miss du cache

#### Jour 21 : Optimisations
- [ ] Compression gzip pour HTML/CSS/JS
- [ ] Header `Content-Encoding: gzip`
- [ ] Tests de performance avec ab (Apache Bench)

---

### ✅ Semaine 4 : Redirections et finalisation (7-9 jours)

#### Jour 22-23 : Redirections HTTP
- [ ] Implémenter `handlers/redirect.py`
- [ ] Charger les redirections depuis `config.json`
- [ ] Gérer 301 et 302
- [ ] Tester : `curl -L http://localhost:4610/old`
- [ ] Redirections conditionnelles (ex: si non authentifié)

#### Jour 24-25 : Logging et monitoring
- [ ] Implémenter logging avec `logging` :
  - [ ] Requêtes reçues
  - [ ] Réponses envoyées (code, taille)
  - [ ] Erreurs
- [ ] Format style Apache : `127.0.0.1 - - [date] "GET / HTTP/1.1" 200 1234`
- [ ] Statistiques en temps réel (nombre de requêtes, latence)

#### Jour 26-27 : Tests et validation
- [ ] Tests unitaires complets :
  - [ ] Parser HTTP
  - [ ] Fichiers statiques
  - [ ] Exécution PHP
  - [ ] Cache
  - [ ] Redirections
- [ ] Tests d'intégration end-to-end
- [ ] Tests de charge avec `ab` ou `wrk`

#### Jour 28-29 : Documentation et démo
- [ ] Compléter le README.md
- [ ] Ajouter des exemples d'utilisation
- [ ] Créer un site de démo complet dans `www/`
- [ ] Vidéo de présentation (optionnel)

#### Jour 30 : Améliorations finales
- [ ] Revue de code
- [ ] Refactoring
- [ ] Optimisations finales
- [ ] Features bonus :
  - [ ] Support HTTPS (SSL/TLS)
  - [ ] WebSockets
  - [ ] Upload de fichiers
  - [ ] Authentification basique

---

## 🚀 Installation et lancement

### Prérequis
```bash
# Python 3.8+
python3 --version

# PHP-CGI
sudo apt install php-cgi  # Debian/Ubuntu
brew install php          # macOS

# Vérifier
which php-cgi
php-cgi -v
```

### Lancement
```bash
cd serveur-cURL
python3 server.py
```

### Tests
```bash
# Test simple
curl http://localhost:4610/

# Test PHP
curl http://localhost:4610/index.php?user=john

# Test API JSON
curl http://localhost:4610/api/users.php

# Test avec headers
curl -v http://localhost:4610/style.css
```

---

## 📚 Ressources utiles

### Documentation officielle
- [asyncio Python](https://docs.python.org/3/library/asyncio.html)
- [RFC 2616 - HTTP/1.1](https://www.rfc-editor.org/rfc/rfc2616)
- [CGI Specification](https://www.rfc-editor.org/rfc/rfc3147)
- [PHP CGI](https://www.php.net/manual/fr/install.unix.commandline.php)

### Tutoriels
- [Build HTTP server in Python](https://realpython.com/python-sockets/)
- [Understanding CGI](https://www.tutorialspoint.com/python/python_cgi_programming.htm)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

### Outils de test
```bash
# Apache Bench - tests de charge
ab -n 1000 -c 10 http://localhost:4610/

# wrk - alternative moderne
wrk -t4 -c100 -d30s http://localhost:4610/

# curl - tests manuels
curl -v http://localhost:4610/
```

---

## 🎯 Objectifs d'apprentissage

À la fin de ce projet, vous maîtriserez :
1. ✅ La programmation asynchrone avec asyncio
2. ✅ Le protocole HTTP en profondeur
3. ✅ L'architecture client-serveur
4. ✅ L'interfaçage avec des programmes externes (CGI)
5. ✅ Les stratégies de cache
6. ✅ La gestion de configurations
7. ✅ Les tests et le debugging réseau

---

## 🐛 Problèmes courants et solutions

### PHP-CGI ne se lance pas
```bash
# Vérifier le chemin
which php-cgi

# Tester manuellement
echo "<?php echo 'test'; ?>" | php-cgi
```

### Port déjà utilisé
```bash
# Trouver le processus
lsof -i :4610

# Tuer le processus
kill -9 <PID>
```

### Performances lentes
- Vérifier le cache (logs)
- Profiler avec `cProfile`
- Utiliser `asyncio.gather()` pour paralléliser

### Erreurs de parsing HTTP
- Vérifier les `\r\n` (CRLF, pas juste `\n`)
- Logger les requêtes brutes
- Tester avec `netcat` : `nc localhost 4610`

---

## 📊 Métriques de succès

- [ ] Supporte 100+ connexions simultanées
- [ ] Latence < 50ms pour fichiers statiques
- [ ] Cache hit rate > 80%
- [ ] Exécution PHP fonctionnelle
- [ ] 0 crash sur 1000 requêtes
- [ ] Code couvert à 70%+ par les tests

---

## 🔮 Extensions futures

- Support HTTP/2
- WebSockets pour chat en temps réel
- Base de données (SQLite)
- Sessions et cookies
- Templating (Jinja2)
- Rate limiting
- Reverse proxy
- Load balancing

--- 

**Bon courage pour votre projet ! 🚀**
 