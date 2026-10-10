<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$method = $_SERVER['REQUEST_METHOD'];

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

$rawBody = file_get_contents('php://input');
$body = json_decode($rawBody, true);

require_once("core/Database.php"); // Database Conenction

if ($method === 'GET' && $uri === '/health-check') {

    http_response_code(200);

    echo json_encode([
        'success' => true,
        'data' => [
            'language' => 'php'
        ],
        'message' => 'API online'
    ]);

} else if ($method === 'GET' && $uri === '/moods') {
    require_once("models/moodsselect.php");
    http_response_code(200);

    echo json_encode([
        'success' => true,
        'data' => $Elements,
        'message' => 'Todo bien'
    ]);

} else if ($method === 'POST' && $uri === '/moods') {
    require_once("models/moodspost.php");
    http_response_code(201);

    echo json_encode([
        'success' => true,
        'data' => $MoodId,
        'message' => 'Todo bien'
    ]);

} else {

    http_response_code(404);

    echo json_encode([
        'success' => false,
        'data' => null,
        'message' => 'Not Found', 
        'debug' => [
            'method' => $method,
            'uri' => $uri,
            'body' => $body
        ]
    ]);
}
?>