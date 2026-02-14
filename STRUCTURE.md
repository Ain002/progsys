# 📁 Structure du Projet

```
serveur-cURL/
│
├── 📄 server.py                    # Serveur HTTP principal
├── 📄 config.json                  # Configuration (redirections)
├── 📘 README.md                    # Documentation principale
├── 📘 MYSQL_SETUP.md               # Guide MySQL/XAMPP
│
├── 📂 handlers/                    # Gestionnaires de requêtes
│   ├── __init__.py
│   ├── database.py                 # ⭐ Connexion MySQL + execute_query()
│   ├── api_sql.py                  # ⭐ API REST pour SQL
│   ├── php_cgi.py                  # Support PHP
│   ├── cache.py                    # Cache LRU
│   ├── monitoring.py               # Statistiques serveur
│   ├── monitoring_widget.py        # Dashboard HTML
│   ├── static.py                   # Fichiers statiques
│   ├── redirect.py                 # Redirections HTTP
│   └── directory_listing.py        # Listing de dossiers
│
├── 📂 utils/                       # Utilitaires
│   ├── __init__.py
│   ├── http_parser.py              # Parser HTTP
│   └── mime_types.py               # Types MIME
│
└── 📂 www/                         # Documents web
    ├── index.html                  # Page d'accueil
    ├── index.php                   # Page PHP
    ├── test.php                    # Test PHP
    │
    ├── 📂 static/                  # Ressources statiques
    │   ├── css/
    │   │   ├── style.css
    │   │   └── test.css
    │   ├── js/
    │   │   ├── main.js
    │   │   └── test.js
    │   └── images/
    │       └── test.svg
    │
    └── 📂 api/                     # API endpoints
        └── test.php
```

## 🔑 Fichiers essentiels

### Serveur
- **server.py** : Point d'entrée, gestion des connexions, routing
- **config.json** : Configuration des redirections

### Base de données (⭐ Important)
- **handlers/database.py** : 
  - `DB_CONFIG` : Configuration MySQL (host, user, password, db)
  - `init_db()` : Initialisation du pool de connexions
  - `execute_query(sql, params)` : Exécute n'importe quelle requête SQL

- **handlers/api_sql.py** : 
  - Route `/api/sql` en POST
  - Reçoit JSON `{sql: string, params: array}`
  - Retourne JSON `{success: bool, result: {rows, rowcount, lastrowid}}`

### Cache & Performance
- **handlers/cache.py** : Cache LRU pour fichiers statiques
- **handlers/monitoring.py** : Collecte de statistiques (latence, requêtes, cache)

### Gestion de contenu
- **handlers/php_cgi.py** : Exécute les scripts PHP
- **handlers/static.py** : Sert les fichiers statiques (HTML, CSS, JS, images)
- **handlers/redirect.py** : Gère les redirections 301/302

### Utilitaires
- **utils/http_parser.py** : Parse les requêtes HTTP brutes
- **utils/mime_types.py** : Détermine le Content-Type des fichiers

## 🚀 Flux de traitement d'une requête

```
1. Client envoie requête HTTP
   ↓
2. server.py : handle_request()
   - Lecture des headers
   - Lecture du body (si POST/PUT)
   - Parsing HTTP
   ↓
3. Routing selon path_only:
   - /_monitor → monitoring_widget.py
   - /api/sql → api_sql.py → database.py
   - *.php → php_cgi.py
   - fichiers → cache.py → static.py
   ↓
4. Réponse HTTP construite et envoyée
   ↓
5. Monitoring : enregistrement des stats
```

## 📊 Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/_monitor` | GET | Dashboard de monitoring HTML |
| `/_monitor/api` | GET | Statistiques JSON |
| `/api/sql` | POST | Exécuter requêtes SQL |
| `/*.php` | GET/POST | Scripts PHP |
| `/*` | GET | Fichiers statiques |

## 🔧 Configuration

### Base de données
Modifier `handlers/database.py` :
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'db': 'serveur_db',
    'charset': 'utf8mb4'
}
```

### Serveur
Modifier `server.py` (lignes ~40-50) :
```python
PORT = 4610
DOCUMENT_ROOT = 'www'
PHP_ENABLED = True
```

## 📝 Notes

- Les paramètres SQL utilisent `?` (converti automatiquement en `%s` pour MySQL)
- Le cache utilise LRU avec limite de 100 fichiers
- Les connexions MySQL utilisent un pool (1-10 connexions)
- Le serveur est asynchrone (gère plusieurs clients en parallèle)
