# 🐘 Intégrer un projet PHP dans le serveur

Ce guide explique comment adapter n'importe quel projet PHP pour qu'il fonctionne avec votre serveur.

## 📁 Structure d'un projet PHP typique

Placez votre projet dans `/www/votre_projet/` :

```
www/
├── votre_projet/
│   ├── index.php          # Page principale
│   ├── traitement.php     # Traitement des formulaires
│   ├── fonction.php       # Fonctions métier
│   └── config.php         # Configuration (optionnel)
```

## 🔧 Configuration de la base de données

### Méthode 1 : PDO (Recommandé)

```php
<?php
// fonction.php ou config.php
function getConnection() {
    $host = '127.0.0.1';          // Utiliser 127.0.0.1 au lieu de localhost (force TCP/IP)
    $port = 3306;
    $dbname = 'serveur_db';       // Votre base de données
    $username = 'root';            // XAMPP par défaut
    $password = '';                // XAMPP par défaut
    
    try {
        $pdo = new PDO(
            "mysql:host=$host;port=$port;dbname=$dbname;charset=utf8", 
            $username, 
            $password
        );
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch(PDOException $e) {
        die("Erreur de connexion : " . $e->getMessage());
    }
}
?>
```

**⚠️ Important** : Utilisez `127.0.0.1` au lieu de `localhost` pour forcer la connexion TCP/IP et éviter l'erreur "No such file or directory" avec XAMPP.

### Méthode 2 : MySQLi

```php
<?php
$conn = new mysqli('localhost', 'root', '', 'serveur_db');

if ($conn->connect_error) {
    die("Connexion échouée: " . $conn->connect_error);
}

$conn->set_charset("utf8mb4");
?>
```

## 📊 Exemple de CRUD complet

Le projet `www/api/test_prog_sys/` est un exemple complet de CRUD. Voici la structure :

### 1. Fonctions CRUD (fonction.php)

```php
<?php
// CREATE
function createUser($name) {
    $pdo = getConnection();
    $sql = "INSERT INTO user (name) VALUES (:name)";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':name', $name);
    return $stmt->execute();
}

// READ ALL
function getAllUsers() {
    $pdo = getConnection();
    $sql = "SELECT * FROM user ORDER BY id DESC";
    $stmt = $pdo->query($sql);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// READ ONE
function getUserById($id) {
    $pdo = getConnection();
    $sql = "SELECT * FROM user WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':id', $id, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

// UPDATE
function updateUser($id, $name) {
    $pdo = getConnection();
    $sql = "UPDATE user SET name = :name WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':name', $name);
    $stmt->bindParam(':id', $id, PDO::PARAM_INT);
    return $stmt->execute();
}

// DELETE
function deleteUser($id) {
    $pdo = getConnection();
    $sql = "DELETE FROM user WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':id', $id, PDO::PARAM_INT);
    return $stmt->execute();
}
?>
```

### 2. Traitement des formulaires (traitement.php)

```php
<?php
require_once 'fonction.php';
session_start();

// CREATE
if ($_POST['action'] === 'create' && !empty($_POST['name'])) {
    if (createUser($_POST['name'])) {
        $_SESSION['message'] = "Ajout réussi";
        $_SESSION['type'] = "success";
    }
    header('Location: index.php');
    exit();
}

// UPDATE
if ($_POST['action'] === 'update') {
    if (updateUser($_POST['id'], $_POST['name'])) {
        $_SESSION['message'] = "Modification réussie";
        $_SESSION['type'] = "success";
    }
    header('Location: index.php');
    exit();
}

// DELETE
if ($_GET['action'] === 'delete' && isset($_GET['id'])) {
    if (deleteUser($_GET['id'])) {
        $_SESSION['message'] = "Suppression réussie";
        $_SESSION['type'] = "success";
    }
    header('Location: index.php');
    exit();
}
?>
```

### 3. Interface utilisateur (index.php)

```php
<?php
require_once 'fonction.php';
session_start();

$users = getAllUsers();

// Récupérer l'utilisateur à modifier
$userToEdit = null;
if (isset($_GET['edit'])) {
    $userToEdit = getUserById($_GET['edit']);
}

// Afficher le message flash
$message = $_SESSION['message'] ?? '';
$messageType = $_SESSION['type'] ?? '';
unset($_SESSION['message'], $_SESSION['type']);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>CRUD Utilisateurs</title>
</head>
<body>
    <!-- Afficher le message -->
    <?php if ($message): ?>
        <div class="<?php echo $messageType; ?>">
            <?php echo htmlspecialchars($message); ?>
        </div>
    <?php endif; ?>

    <!-- Formulaire CREATE/UPDATE -->
    <form method="POST" action="traitement.php">
        <?php if ($userToEdit): ?>
            <input type="hidden" name="action" value="update">
            <input type="hidden" name="id" value="<?php echo $userToEdit['id']; ?>">
            <input type="text" name="name" value="<?php echo htmlspecialchars($userToEdit['name']); ?>" required>
            <button>Modifier</button>
        <?php else: ?>
            <input type="hidden" name="action" value="create">
            <input type="text" name="name" required>
            <button>Ajouter</button>
        <?php endif; ?>
    </form>

    <!-- Liste -->
    <table>
        <tr><th>ID</th><th>Nom</th><th>Actions</th></tr>
        <?php foreach ($users as $user): ?>
            <tr>
                <td><?php echo $user['id']; ?></td>
                <td><?php echo htmlspecialchars($user['name']); ?></td>
                <td>
                    <a href="index.php?edit=<?php echo $user['id']; ?>">Modifier</a>
                    <a href="traitement.php?action=delete&id=<?php echo $user['id']; ?>" 
                       onclick="return confirm('Supprimer ?')">Supprimer</a>
                </td>
            </tr>
        <?php endforeach; ?>
    </table>
</body>
</html>
```

## ✅ Checklist d'intégration

Pour intégrer un projet PHP existant :

- [ ] Placer le projet dans `/www/votre_projet/`
- [ ] Adapter la connexion à la base de données
  - Host : `localhost`
  - User : `root`
  - Password : `` (vide pour XAMPP)
  - Database : `serveur_db` (ou votre base)
- [ ] Vérifier que les noms de colonnes correspondent
  - Le serveur Python utilise `name` (pas `nom`)
  - Adapter les requêtes SQL si nécessaire
- [ ] Tester l'accès : `http://localhost:4610/votre_projet/`
- [ ] Vérifier les sessions PHP (le serveur les supporte)
- [ ] Vérifier les redirections (`header('Location: ...')`)

## 🔍 Débogage

### Erreur de connexion MySQL

```
Erreur de connexion : SQLSTATE[HY000] [2002] No such file or directory
```

**Cause** : PHP cherche le socket Unix de MySQL mais ne le trouve pas.

**Solution** : Utiliser `127.0.0.1` au lieu de `localhost` dans la connexion PDO :

```php
// ❌ MAUVAIS (cherche le socket Unix)
$pdo = new PDO("mysql:host=localhost;dbname=serveur_db", "root", "");

// ✅ BON (utilise TCP/IP)
$pdo = new PDO("mysql:host=127.0.0.1;port=3306;dbname=serveur_db", "root", "");
```

**Autre solution** : Spécifier le chemin du socket XAMPP :

```php
$pdo = new PDO(
    "mysql:unix_socket=/opt/lampp/var/mysql/mysql.sock;dbname=serveur_db",
    "root",
    ""
);
```

### Autre erreur de connexion

```
Erreur de connexion : SQLSTATE[HY000] [2002] Connection refused
```

**Solutions** :
- Vérifier que MySQL/XAMPP est démarré
- Vérifier les paramètres dans `fonction.php`
- Tester la connexion en ligne de commande : `mysql -u root -p`

### Erreur "Column not found"

```
SQLSTATE[42S22]: Column not found: 1054 Unknown column 'nom'
```

**Solution** : Votre table utilise `name` mais votre code utilise `nom`. Uniformiser.

### Sessions ne fonctionnent pas

**Solution** : Vérifier que `session_start()` est appelé au début de chaque page PHP.

## 📦 Structure de table recommandée

```sql
CREATE TABLE user (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Accès au projet

Une fois intégré, accédez à votre projet via :

```
http://localhost:4610/votre_projet/index.php
```

Exemple avec le projet de démonstration :

```
http://localhost:4610/api/test_prog_sys/index.php
```

## 💡 Avantages de ce serveur

✅ Support PHP-CGI complet
✅ Sessions PHP fonctionnelles
✅ Connexion MySQL/MariaDB native
✅ Cache pour les fichiers statiques
✅ Monitoring intégré
✅ Pas de configuration Apache/Nginx nécessaire

## 🔗 Combiner PHP et API Python

Vous pouvez même appeler l'API Python depuis PHP :

```php
<?php
// Appeler l'API Python depuis PHP
$data = [
    'sql' => 'SELECT * FROM user',
    'params' => []
];

$ch = curl_init('http://localhost:4610/api/sql');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$result = json_decode($response, true);

print_r($result['result']['rows']);
?>
```
