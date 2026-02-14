# 🌐 Serveur HTTP Python avec MySQL

Serveur HTTP asynchrone avec intégration MySQL pour vos applications web.

## ✨ Fonctionnalités

- ✅ **Serveur HTTP asynchrone** (asyncio)
- ✅ **API REST MySQL** - Exécuter des requêtes SQL via HTTP
- ✅ **Support PHP-CGI** - Scripts PHP dynamiques
- ✅ **Cache LRU intelligent** - Performance optimale
- ✅ **Monitoring temps réel** - Statistiques du serveur
- ✅ **Fichiers statiques** - HTML, CSS, JS, images

## 📦 Installation

```bash
# 1. Installer la dépendance MySQL
pip3 install aiomysql --break-system-packages

# 2. Configurer votre base de données
# Éditer handlers/database.py - section DB_CONFIG
```

Voir [MYSQL_SETUP.md](MYSQL_SETUP.md) pour la configuration MySQL/XAMPP.

## 🚀 Démarrage

```bash
python3 server.py
```

Serveur disponible sur `http://localhost:4610`

## 📁 Structure du projet

```
serveur-cURL/
├── server.py              # Serveur HTTP principal
├── config.json            # Configuration (redirections)
│
├── handlers/              # Gestionnaires de requêtes
│   ├── database.py        # Connexion MySQL
│   ├── api_sql.py         # API REST pour SQL
│   ├── php_cgi.py         # Support PHP
│   ├── cache.py           # Système de cache
│   ├── monitoring.py      # Stats serveur
│   └── ...
│
├── utils/                 # Utilitaires
│   ├── http_parser.py     # Parser HTTP
│   └── mime_types.py      # Types MIME
│
└── www/                   # Documents web
    ├── index.html         # Page d'accueil
    ├── static/            # CSS, JS, images
    └── api/               # API endpoints
```

## 🔌 Utilisation de l'API MySQL

### Depuis JavaScript (fetch)

```javascript
// Exécuter une requête SQL
const response = await fetch('http://localhost:4610/api/sql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        sql: 'SELECT * FROM user WHERE id = ?',
        params: [5]
    })
});

const data = await response.json();
console.log(data.result.rows); // Résultats
```

### Depuis PHP (projet classique)

Un projet PHP complet est disponible dans `www/api/test_prog_sys/` :

```php
// fonction.php - Connexion MySQL avec PDO
function getConnection() {
    $pdo = new PDO("mysql:host=localhost;dbname=serveur_db", "root", "");
    return $pdo;
}

// Utiliser les fonctions CRUD
createUser("John");           // INSERT
$users = getAllUsers();       // SELECT
updateUser(1, "Jane");        // UPDATE
deleteUser(1);                // DELETE
```

**Accès** : `http://localhost:4610/api/test_prog_sys/index.php`

### Exemples de requêtes

```javascript
// INSERT
fetch('/api/sql', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sql: 'INSERT INTO products (name, price) VALUES (?, ?)',
        params: ['Laptop', 999.99]
    })
});

// UPDATE
fetch('/api/sql', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sql: 'UPDATE user SET name = ? WHERE id = ?',
        params: ['John', 1]
    })
});

// DELETE
fetch('/api/sql', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sql: 'DELETE FROM user WHERE id = ?',
        params: [5]
    })
});

// SELECT avec JOIN
fetch('/api/sql', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sql: 'SELECT u.name, o.total FROM user u JOIN orders o ON u.id = o.user_id',
        params: []
    })
});
```

## 📊 Monitoring

Accédez au dashboard : `http://localhost:4610/_monitor`

## ⚙️ Configuration

### Base de données (handlers/database.py)

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

### Serveur (server.py)

```python
PORT = 4610
DOCUMENT_ROOT = 'www'
PHP_ENABLED = True
```

## 🛠️ Dépannage

**Port déjà utilisé :**
```bash
pkill -f "python3 server.py"
```

**Erreur MySQL :**
- Vérifier que MySQL/XAMPP est démarré
- Vérifier les paramètres dans `handlers/database.py`
- Voir [MYSQL_SETUP.md](MYSQL_SETUP.md)

## 📝 Licence

Projet éducatif - 2026
