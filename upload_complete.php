<?php 
//セッションを開始する
session_start();
session_regenerate_id(true);

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>アップローダー</title>
<link href="common/css/import.css" rel="stylesheet" type="text/css" />
</head>

<body>
<div id="container">
<div id="header">
<h1>アップローダー</h1>
</div>
<div class="breadcrumb"><a href="http://php-fan.org/">HOME</a> > アップローダー</div>
<div id="content">
<p class="txtbig"><p><?php echo $_SESSION['complete'];
$_SESSION = array();
?></p>
<form id="form1" name="form1" method="post" action="uploader.php">
  <input type="submit" name="button" id="button" value="戻る" />
</form>
</div>
<div id="copy">Copyright(C)<?php echo date("Y");?> PHP-FAN.ORG All Right Reserved. </div>
</div>

</body>
</html>
