// JavaScript pour le serveur HTTP

console.log('Serveur HTTP - Client JavaScript chargé');

// Test de l'API
async function testAPI() {
    try {
        const response = await fetch('/api/test.php');
        const data = await response.json();
        console.log('Réponse API:', data);
    } catch (error) {
        console.error('Erreur API:', error);
    }
}

// Appeler au chargement
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page chargée, prêt !');
    // testAPI(); // Décommenter pour tester l'API
});
