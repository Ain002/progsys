<?php
header('Content-Type: text/plain; charset=utf-8');

echo "=== Test PHP-CGI ===\n\n";
echo "Date: " . date('Y-m-d H:i:s') . "\n";
echo "PHP Version: " . phpversion() . "\n";
echo "Méthode: " . $_SERVER['REQUEST_METHOD'] . "\n\n";

if ($_SERVER['REQUEST_METHOD'] === 'GET' && !empty($_GET)) {
    echo "=== Paramètres GET ===\n";
    foreach ($_GET as $key => $value) {
        echo "$key = " . htmlspecialchars($value) . "\n";
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST)) {
    echo "=== Données POST ===\n";
    foreach ($_POST as $key => $value) {
        echo "$key = " . htmlspecialchars($value) . "\n";
    }
}

if (empty($_GET) && empty($_POST)) {
    echo "Aucun paramètre reçu.\n";
    echo "Testez avec: test.php?nom=Alice&age=25\n";
}

echo "\n✓ PHP-CGI fonctionne correctement!\n";
?>
