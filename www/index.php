<?php
// Page PHP de test

header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Page PHP - Serveur HTTP</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <h1>Page PHP fonctionnelle !</h1>
    
    <h2>Informations serveur</h2>
    <p><strong>Date/Heure :</strong> <?php echo date('d/m/Y H:i:s'); ?></p>
    <p><strong>Version PHP :</strong> <?php echo phpversion(); ?></p>
    
    <h2>Variables GET</h2>
    <pre><?php print_r($_GET); ?></pre>
    
    <h2>Variables serveur</h2>
    <pre><?php 
        echo "REQUEST_METHOD: " . ($_SERVER['REQUEST_METHOD'] ?? 'N/A') . "\n";
        echo "QUERY_STRING: " . ($_SERVER['QUERY_STRING'] ?? 'N/A') . "\n";
        echo "SCRIPT_NAME: " . ($_SERVER['SCRIPT_NAME'] ?? 'N/A') . "\n";
    ?></pre>
    
    <p><a href="/">Retour à l'accueil</a></p>
</body>
</html>
