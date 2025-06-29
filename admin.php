<?php
// admin.php - Liệt kê toàn bộ file JSON đã lưu

$files = glob("data_*.json");

echo "<h2>📁 Danh sách dữ liệu người dùng:</h2><ul>";
foreach ($files as $f) {
    $uid = str_replace(["data_", ".json"], "", $f);
    echo "<li><b>$uid</b> ➜ 
        <a href='get.php?uid=$uid'>[Xem]</a> • 
        <a href='delete.php?uid=$uid' onclick='return confirm(\"Xoá dữ liệu của $uid?\")'>[Xoá]</a>
    </li>";
}
echo "</ul>";
?>