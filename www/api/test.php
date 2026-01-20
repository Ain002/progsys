<?php
// API de test retournant du JSON

header('Content-Type: application/json');

$response = [
    'status' => 'success',
    'message' => 'API PHP fonctionnelle',
    'timestamp' => time(),
    'date' => date('Y-m-d H:i:s'),
    'method' => $_SERVER['REQUEST_METHOD'] ?? 'UNKNOWN',
    'data' => [
        'users' => ['Alice', 'Bob', 'Charlie'],
        'version' => '1.0.0'
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
