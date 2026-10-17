<?php
require_once("config/headers.php");

$method = $_SERVER['REQUEST_METHOD'];

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$resourceId = explode('/', $uri)[2] ?? null;

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
        'message' => 'Todo bien',
        'debug' => [
            'method' => $_SERVER['REQUEST_METHOD'],
            'uri' => $_SERVER['REQUEST_URI'],
            'body' => $body
        ]
    ]);

} else if ($method === 'POST' && $uri === '/moods') {
    require_once("models/moodspost.php");
    http_response_code(201);

    echo json_encode([
        'success' => true,
        'data' => $MoodId,
        'message' => 'Todo bien',
        'debug' => [
            'method' => $_SERVER['REQUEST_METHOD'],
            'uri' => $_SERVER['REQUEST_URI'],
            'body' => $body
        ]
    ]);

} else if ($method === 'PUT' && $uri === '/moods/' . $resourceId) {
    require_once("models/moodsput.php");
    http_response_code(200);

    echo json_encode([
        'success' => true,
        'data' => $newData,
        'message' => 'Todo bien'
    ]);

} else if ($method === 'DELETE' && $uri === '/moods/' . $resourceId) {
    require_once("models/moodsdelete.php");
    http_response_code(200);

    echo json_encode([
        'success' => true,
        'data' => $newData,
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

addRoutes($request);
?>