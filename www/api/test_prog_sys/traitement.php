<?php
require_once 'fonction.php';

session_start();

// Traitement CREATE
if (isset($_POST['action']) && $_POST['action'] === 'create') {
    if (!empty($_POST['name'])) {
        if (createUser($_POST['name'])) {
            $_SESSION['message'] = "Utilisateur ajouté avec succès";
            $_SESSION['type'] = "success";
        } else {
            $_SESSION['message'] = "Erreur lors de l'ajout";
            $_SESSION['type'] = "error";
        }
    }
    header('Location: /api/test_prog_sys/index.php');
    exit();
}

// Traitement UPDATE
if (isset($_POST['action']) && $_POST['action'] === 'update') {
    if (!empty($_POST['id']) && !empty($_POST['name'])) {
        if (updateUser($_POST['id'], $_POST['name'])) {
            $_SESSION['message'] = "Utilisateur modifié avec succès";
            $_SESSION['type'] = "success";
        } else {
            $_SESSION['message'] = "Erreur lors de la modification";
            $_SESSION['type'] = "error";
        }
    }
    header('Location: /api/test_prog_sys/index.php');
    exit();
}

// Traitement DELETE
if (isset($_GET['action']) && $_GET['action'] === 'delete' && isset($_GET['id'])) {
    if (deleteUser($_GET['id'])) {
        $_SESSION['message'] = "Utilisateur supprimé avec succès";
        $_SESSION['type'] = "success";
    } else {
        $_SESSION['message'] = "Erreur lors de la suppression";
        $_SESSION['type'] = "error";
    }
    header('Location: /api/test_prog_sys/index.php');
    exit();
}

// Si aucune action valide
header('Location: /api/test_prog_sys/index.php');
exit();
?>