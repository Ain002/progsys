# 🗄️ Guide MySQL pour le Serveur

## Option 1: Avec XAMPP (Recommandé si déjà installé)

### Démarrer XAMPP
```bash
# Via l'interface XAMPP ou:
sudo /opt/lampp/lampp startmysql
```

### Configuration de la base de données
1. Ouvrir phpMyAdmin: `http://localhost/phpmyadmin`
2. Cliquer sur "Nouvelle base de données"
3. Nom: `serveur_db`
4. Encodage: `utf8mb4_general_ci`
5. Créer

### Configuration du serveur

XAMPP utilise par défaut:
- **User**: `root`
- **Password**: `` (vide)
- **Port**: `3306`

Dans `handlers/database.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',        # Utilisateur XAMPP par défaut
    'password': '',        # Pas de mot de passe par défaut
    'db': 'serveur_db'
}
```

---

## Option 2: MySQL/MariaDB natif

### Installation
```bash
# Installer MariaDB
sudo apt install mariadb-server

# Démarrer le service
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Sécuriser l'installation
sudo mysql_secure_installation
```

### Configuration de la base de données
```bash
# Se connecter en root
sudo mysql

# Créer la base de données
CREATE DATABASE serveur_db;

# Créer l'utilisateur
CREATE USER 'serveur_user'@'localhost' IDENTIFIED BY 'password123';

# Donner les permissions
GRANT ALL PRIVILEGES ON serveur_db.* TO 'serveur_user'@'localhost';
FLUSH PRIVILEGES;

# Quitter
EXIT;
```

Dans `handlers/database.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'serveur_user',
    'password': 'password123',
    'db': 'serveur_db'
}
```

---

## Installation du driver Python

```bash
pip install aiomysql
```

## Utilisation

### Via l'interface web
Accédez à `http://localhost:4610/test_database.html`

### Via API REST
```bash
curl -X POST http://localhost:4610/api/sql \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users"}'
```

### Exemples de requêtes

```sql
-- Créer une table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100)
);

-- Insérer des données
INSERT INTO users (nom, email) VALUES ('Alice', 'alice@test.com');
INSERT INTO users (nom, email) VALUES ('Bob', 'bob@test.com');

-- Sélectionner
SELECT * FROM users;
SELECT * FROM users WHERE nom = 'Alice';

-- Mettre à jour
UPDATE users SET nom = 'Alice Smith' WHERE id = 1;

-- Supprimer
DELETE FROM users WHERE id = 2;

-- Modifier la structure
ALTER TABLE users ADD COLUMN age INT;

-- Informations
SHOW TABLES;
DESCRIBE users;
```

## Sécurité

⚠️ **Important** : Dans un environnement de production:
- Utilisez des requêtes préparées (déjà implémenté avec `params`)
- Limitez les permissions de l'utilisateur DB
- N'exposez pas l'API SQL publiquement
- Ajoutez une authentification
- Validez toutes les entrées

## Dépannage

### Connexion refusée
```bash
# Vérifier que MySQL tourne
sudo systemctl status mariadb

# Redémarrer si nécessaire
sudo systemctl restart mariadb
```

### Erreur d'authentification
```bash
# Réinitialiser le mot de passe
sudo mysql
ALTER USER 'serveur_user'@'localhost' IDENTIFIED BY 'nouveau_password';
FLUSH PRIVILEGES;
```

### Port déjà utilisé
```bash
# Voir qui utilise le port 3306
sudo netstat -tlnp | grep 3306
```
