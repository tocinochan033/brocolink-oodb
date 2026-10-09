<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$method = $_SERVER['REQUEST_METHOD'];

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

$rawBody = file_get_contents('php://input');
$body = json_decode($rawBody, true);

if ($method === 'GET' && $uri === '/health-check') {

    http_response_code(200);

    echo json_encode([
        'success' => true,
        'data' => [
            'language' => 'php'
        ],
        'message' => 'API online'
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