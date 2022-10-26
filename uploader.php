<?php 

//セッションを開始する
session_start();
session_regenerate_id(true);
//変数初期化
$message = "";
//ワンタイムチケット比較、同じなら実行
if (isset($_POST['ticket'],$_SESSION['ticket']) && $_POST['ticket'] === $_SESSION['ticket']) {
	sleep(1);
	//登録ボタンを押したら
	if(isset($_POST['reg'])){
	
		if ($_POST['name'] == "" ){
		
			$message = "名前を入力してください。";
			
		}else{
		
			define("UP_DIR", "./temp/");
			
			for ($i = 0; $i < count(@$_FILES['datafile']['name']); $i++) {
			
				if (strlen($_FILES['datafile']['name'][$i]) > 0) {
				
    				$extension = "";
				
					$allow_extension = array('jpg','png','gif','ai','psd','pdf','eps','zip','lzh','xls','doc','ppt');	//許可拡張子 小文字（それ以外はエラー）
			
					$path = pathinfo($_FILES['datafile']['name'][$i]);
				
					$extension = $path['extension'];//拡張子取得

					$extension = strtolower($extension);//小文字化
	
					if(!in_array($extension, $allow_extension)){
				
						$message = "そのファイル形式はアップロードできません。";
				
    				}elseif ($_FILES['datafile']['size'][$i] > 1002400) {
	
	      				$message = "ファイルサイズが大きすぎます。1MB以下にしてください";
							
    				}else{
					
						$number = mt_rand(100,999);//3桁ランダム数字
			
						$date = date("Ymd");//現在の年月日取得
				
						// ここでは格納ディレクトリの下に「"Data" + 現在の年月日 + 3桁のランダム数字 + 連番 + 拡張子」で配置します。
						$datafile = 'Data' . $date . '_' . $number . $i . '.' . $extension;
											
						if (move_uploaded_file($_FILES['datafile']['tmp_name'][$i], UP_DIR . $datafile)) {   		
					
							$_SESSION['datafile'][$i] = $datafile;//ファイル名保持
							$complete = "ok";
						
						}else{
						
							$message = "アップロードに失敗しました。もう一度やり直して下さい。";      						
						
						}
      				}
					
				}else{
				
					$message = "ファイルを選択して下さい。";
					
				}
			}
			
			if(isset($complete) && $complete == "ok"){
				$name = $_POST['name'];
				$_SESSION['complete'] = "{$name}さん、ファイルアップロード完了しました！！";
				header("Location:  upload_complete.php" );
				exit;
			}	
		}
	}		
}
//ワンタイムトークン取得
$_SESSION['ticket'] = md5(uniqid(mt_rand(), true));


?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>アップローダー</title>
<link href="common/css/import.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="common/js/jquery.js"></script>
<script type="text/javascript">
<!--
$(function(){
	$('#btnsend').click(
		function() {
			$('#loading').html('通信中...');
			$('#loading').show();
	});
});
//-->
</script>
</head>

<body>
<div id="container">
<div id="header">
<h1>アップローダー</h1>
</div>
<div class="breadcrumb"><a href="http://php-fan.org/">HOME</a> > アップローダー</div>
<div id="content">
<form method="post" action="<?php echo $_SERVER['PHP_SELF']?>" name="data" enctype="multipart/form-data">
<input type="hidden" name="ticket" value="<?php echo $_SESSION['ticket'];?>" />
<div class="txtbig"><?php if(!empty($message)){	echo $message;}?></div>
<div id="loading"></div>
<table class="table_01">
<tr>
<td colspan="2"><span class="text14b">データファイル選択1MBまで</span>（jpg,png,gif,ai,psd,pdf,eps,zip,lzh,xls,doc,ppt）</td>
</tr>
<tr>
<th>名前</th>
<td><input type="text" name="name" id="name" /></td>
</tr>
<tr>
<th>データ1</th>
<td><input type="file" name="datafile[]" /></td>
</tr>
<tr>
<th>データ2</th>
<td><input type="file" name="datafile[]" /></td>
</tr>
<tr>
  <th>データ3</th>
  <td><input type="file" name="datafile[]" /></td>
</tr>
<tr>
  <td colspan="2"><input type="submit" name="reg" value=" 登 録 " id="btnsend" /> <input type="submit" name="cancel" value="キャンセル" /></td>
  </tr>
</table>
</form>
</div>
<div id="copy">Copyright(C)<?php echo date("Y");?> PHP-FAN.ORG All Right Reserved. </div>
</div>

</body>
</html>
