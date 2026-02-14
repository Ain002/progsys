<?php
// Connexion à la base de données
function getConnection() {
    $host = '127.0.0.1';          // Utiliser 127.0.0.1 au lieu de localhost pour forcer TCP/IP
    $port = 3306;
    $dbname = 'serveur_db';
    $username = 'root';
    $password = '';
    
    try {
        // Spécifier le port pour forcer la connexion TCP/IP
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

// CREATE - Ajouter un utilisateur
function createUser($name) {
    $pdo = getConnection();
    $sql = "INSERT INTO user (name) VALUES (:name)";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':name', $name);
    return $stmt->execute();
}

// READ - Lire tous les utilisateurs
function getAllUsers() {
    $pdo = getConnection();
    $sql = "SELECT * FROM user ORDER BY id DESC";
    $stmt = $pdo->query($sql);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// READ - Lire un utilisateur par ID
function getUserById($id) {
    $pdo = getConnection();
    $sql = "SELECT * FROM user WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':id', $id);
    $stmt->execute();
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

// UPDATE - Mettre à jour un utilisateur
function updateUser($id, $name) {
    $pdo = getConnection();
    $sql = "UPDATE user SET name = :name WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':name', $name);
    $stmt->bindParam(':id', $id);
    return $stmt->execute();
}

// DELETE - Supprimer un utilisateur
function deleteUser($id) {
    $pdo = getConnection();
    $sql = "DELETE FROM user WHERE id = :id";
    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':id', $id);
    return $stmt->execute();
}
?>