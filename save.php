<?php
// save.php - Nhận dữ liệu POST và lưu file JSON

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo "⛔ Chỉ chấp nhận POST";
    exit;
}

$data = file_get_contents("php://input");

$uid = $_GET["uid"] ?? "unknown";
$uid_clean = preg_replace("/[^a-zA-Z0-9]/", "_", $uid);
$filename = "data_" . $uid_clean . ".json";

if (file_put_contents($filename, $data)) {
    echo "✅ Đã lưu dữ liệu vào $filename";
} else {
    echo "❌ Lỗi khi lưu file!";
}
?>