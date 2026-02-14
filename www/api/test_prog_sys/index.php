<?php
require_once 'fonction.php';
session_start();

// Récupérer tous les utilisateurs
$users = getAllUsers();

// Récupérer l'utilisateur à modifier si demandé
$userToEdit = null;
if (isset($_GET['edit'])) {
    $userToEdit = getUserById($_GET['edit']);
}

// Afficher les messages
$message = '';
if (isset($_SESSION['message'])) {
    $message = $_SESSION['message'];
    $messageType = $_SESSION['type'];
    unset($_SESSION['message']);
    unset($_SESSION['type']);
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRUD Utilisateurs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; margin-bottom: 20px; }
        h2 { color: #555; margin-top: 30px; margin-bottom: 15px; font-size: 1.2em; }
        .message { padding: 10px; margin-bottom: 20px; border-radius: 3px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        form { margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 3px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"] { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .btn-cancel { background: #6c757d; margin-left: 10px; }
        .btn-cancel:hover { background: #545b62; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007bff; color: white; }
        tr:hover { background: #f5f5f5; }
        .actions a { margin-right: 10px; padding: 5px 10px; text-decoration: none; border-radius: 3px; }
        .btn-edit { background: #ffc107; color: #000; }
        .btn-delete { background: #dc3545; color: white; }
        .btn-edit:hover { background: #e0a800; }
        .btn-delete:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestion des Utilisateurs - CRUD</h1>
        
        <?php if ($message): ?>
            <div class="message <?php echo $messageType; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>

        <!-- Formulaire CREATE ou UPDATE -->
        <?php if ($userToEdit): ?>
            <h2>Modifier un utilisateur</h2>
            <form method="POST" action="traitement.php">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="id" value="<?php echo htmlspecialchars($userToEdit['id']); ?>">
                <label for="name">Nom :</label>
                <input type="text" id="name" name="name" value="<?php echo htmlspecialchars($userToEdit['name']); ?>" required>
                <button type="submit">Modifier</button>
                <a href="index.php"><button type="button" class="btn-cancel">Annuler</button></a>
            </form>
        <?php else: ?>
            <h2>Ajouter un utilisateur</h2>
            <form method="POST" action="traitement.php">
                <input type="hidden" name="action" value="create">
                <label for="name">Nom :</label>
                <input type="text" id="name" name="name" required>
                <button type="submit">Ajouter</button>
            </form>
        <?php endif; ?>

        <!-- Liste des utilisateurs -->
        <h2>Liste des utilisateurs</h2>
        <?php if (count($users) > 0): ?>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nom</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($user['id']); ?></td>
                            <td><?php echo htmlspecialchars($user['name']); ?></td>
                            <td class="actions">
                                <a href="index.php?edit=<?php echo $user['id']; ?>" class="btn-edit">Modifier</a>
                                <a href="traitement.php?action=delete&id=<?php echo $user['id']; ?>" 
                                   onclick="return confirm('Voulez-vous vraiment supprimer cet utilisateur ?')" 
                                   class="btn-delete">Supprimer</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>Aucun utilisateur dans la base de données.</p>
        <?php endif; ?>
    </div>
</body>
</html>