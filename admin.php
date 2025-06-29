<?php
// admin.php – Giao diện điều khiển bot ZProject

// Cập nhật prompt nếu có POST
if ($_SERVER["REQUEST_METHOD"] === "POST" && isset($_POST["new_prompt"])) {
    $prompt_text = trim($_POST["new_prompt"]);
    file_put_contents("prompt.json", json_encode(["prompt" => $prompt_text], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    $status = "✅ Đã cập nhật prompt!";
}

// Đọc prompt hiện tại
$current_prompt = "Chưa có prompt";
if (file_exists("prompt.json")) {
    $json = json_decode(file_get_contents("prompt.json"), true);
    $current_prompt = $json["prompt"] ?? "(không có nội dung)";
}

// Lấy danh sách file
$files = glob("data_*.json");
?>

<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>🧠 Trung tâm điều khiển ZProject</title>
  <style>
    body {
      background: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
      padding: 30px;
    }
    h1 { font-size: 28px; color: #38bdf8; }
    textarea {
      width: 100%; height: 120px;
      background: #1e293b; color: #f8fafc;
      border: 1px solid #334155; border-radius: 6px;
      padding: 10px; font-family: monospace;
    }
    button {
      background: #38bdf8; border: none; padding: 8px 16px;
      color: #0f172a; border-radius: 5px;
      font-weight: bold; cursor: pointer;
      margin-top: 10px;
    }
    ul { list-style: none; padding-left: 0; }
    li {
      background: #1e293b; padding: 10px; margin: 8px 0;
      border: 1px solid #334155; border-radius: 5px;
      display: flex; justify-content: space-between; align-items: center;
    }
    a {
      color: #60a5fa; text-decoration: none;
      margin-left: 12px;
    }
    .status {
      background: #16a34a; padding: 6px 10px;
      border-radius: 4px; display: inline-block;
      margin-bottom: 15px; font-size: 14px;
    }
  </style>
</head>
<body>
  <h1>🧠 Trung tâm điều khiển ZProject Bot</h1>

  <?php if (isset($status)) echo "<div class='status'>$status</div>"; ?>

  <h2>📄 Cấu hình Prompt hiện tại</h2>
  <form method="post">
    <textarea name="new_prompt"><?= htmlspecialchars($current_prompt) ?></textarea>
    <br>
    <button type="submit">💾 Lưu prompt mới</button>
  </form>

  <h2>📁 Dữ liệu người dùng (<?= count($files) ?> file)</h2>
  <ul>
    <?php foreach ($files as $f): 
      $uid = str_replace(["data_", ".json"], "", $f);
    ?>
      <li>
        <b><?= htmlspecialchars($f) ?></b>
        <span>
          <a href="get.php?uid=<?= $uid ?>">[Xem]</a>
          <a href="delete.php?uid=<?= $uid ?>" onclick="return confirm('Xoá dữ liệu của <?= $uid ?>?')">[Xoá]</a>
        </span>
      </li>
    <?php endforeach; ?>
  </ul>
</body>
</html>