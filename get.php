<?php
// get.php?uid=USER_ID

$uid = $_GET["uid"] ?? "";
$filename = "data_" . preg_replace("/[^a-zA-Z0-9]/", "_", $uid) . ".json";

if (!$uid || !file_exists($filename)) {
    http_response_code(404);
    echo "❌ Không tìm thấy dữ liệu.";
    exit;
}

header('Content-Type: application/json');
readfile($filename);
?>