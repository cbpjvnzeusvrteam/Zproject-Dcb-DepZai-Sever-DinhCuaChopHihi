<?php
// delete.php?uid=USER_ID

$uid = $_GET["uid"] ?? "";
$filename = "data_" . preg_replace("/[^a-zA-Z0-9]/", "_", $uid) . ".json";

if (!$uid || !file_exists($filename)) {
    echo "⚠️ Không tìm thấy file để xoá.";
    exit;
}

unlink($filename);
echo "✅ Đã xoá dữ liệu người dùng: $uid";
?>