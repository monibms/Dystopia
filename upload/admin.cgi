#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ UP-LOADER : admin.cgi - 2022/01/10
#│ copyright (c) kentweb, 1997-2022
#│ https://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use vars qw($cgi %in %cf);
use lib "./lib";
use CGI::Minimal;
use CGI::Session;
use Digest::SHA::PurePerl qw(sha256_base64);

# 設定ファイル認識
require "./init.cgi";
%cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
$cgi = CGI::Minimal->new;
error('容量オーバー') if ($cgi->truncated);
%in = parse_form($cgi);

# 認証
require "./lib/login.pl";
auth_login();

# 管理モード
if ($in{data_men}) { data_men(); }
if ($in{dlog_mgr}) { dlog_mgr(); }
if ($in{pass_mgr}) { pass_mgr(); }
menu_html();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	header("メニューTOP");
	print <<EOM;
<div align="center">
<p>選択ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<table class="form-tbl">
<tr>
	<th></th>
	<th width="300">処理メニュー</th>
</tr><tr>
	<td class="ta-c"><input type="submit" name="data_men" value="選択"></td>
	<td>記事データ管理</td>
</tr><tr>
	<td class="ta-c"><input type="submit" name="dlog_mgr" value="選択"></td>
	<td>ダウンロードログ</td>
</tr><tr>
	<td class="ta-c"><input type="submit" name="pass_mgr" value="選択"></td>
	<td>パスワード管理</td>
</tr><tr>
	<td class="ta-c"><input type="submit" name="logoff" value="選択"></td>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  データ画面画面
#-----------------------------------------------------------
sub data_men {
	# 削除処理
	if ($in{del} && $in{no}) {
		
		# 削除情報
		my %del;
		for ( $cgi->param('no') ) { $del{$_}++; }
		
		# 削除情報をマッチング
		my @log;
		open(DAT,"+< $cf{datadir}/log.cgi") or error("open err: log.cgi");
		eval "flock(DAT,2);";
		while (<DAT>) {
			my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
			
			if (defined $del{$no}) {
				unlink("$cf{upldir}/$rand/$fnam.$ex");
				rmdir("$cf{upldir}/$rand");
				next;
			}
			push(@log,$_);
		}
		seek(DAT,0,0);
		print DAT @log;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# カウントファイル削除
		my @log;
		open(DAT,"+< $cf{datadir}/count.dat") or error("open err: count.dat");
		eval "flock(DAT,2);";
		while(<DAT>) {
			my ($no,undef) = split(/:/);
			next if (defined $del{$no});
			push(@log,$_);
		}
		# 更新
		seek(DAT,0,0);
		print DAT @log;
		truncate(DAT,tell(DAT));
		close(DAT);
	
	# パス変更
	} elsif ($in{rename}) {
		if (!$in{no}) { error('変更するファイル名にチェックを入れてください'); }
		
		# ファイル名変更
		file_rename();
	}
	
	# 画面表示
	header("データ画面","js");
	back_btn();
	print <<EOM;
<div id="ttl">■ データ管理</div>
<ul>
<li>チェックボタンをチェックして実行ボタンを押します。
<li>ファイルへの直接リンクを避けるため、ファイルの「パス変更」を行うことができます。
</ul>
<form action="$cf{admin_cgi}" method="post" name="allchk">
<input type="hidden" name="sid" value="$in{sid}">
<input type="hidden" name="data_men" value="1">
<div id="ope-btn">
<input type="submit" name="del" value="削除" class="btn" onclick="return confirm('削除しますか？');">
<input type="submit" name="rename" value="パス変更" class="btn">
</div>
<table class="form-tbl">
<tr>
	<th><input type="button" onclick="allcheck();" value="全選択"></th>
	<th>アップ日時</th>
	<th>ファイル名</th>
	<th>サイズ</th>
</tr>
EOM

	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	while (<IN>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		print qq|<td class="ta-c"><input type="checkbox" name="no" value="$no"></td>|;
		print qq|<td>$date</td>|;
		print qq|<td><a href="$cf{uplurl}/$rand/$fnam.$ex" target="_blank">$fnam.$ex</a></td>|;
		print qq|<td class="ta-r">$size</td></tr>\n|;
	}
	close(IN);
	
	print <<EOM;
</table>
</form>
EOM
	footer();
}

#-----------------------------------------------------------
#  DLログ画面
#-----------------------------------------------------------
sub dlog_mgr {
	my %fnam;
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	while (<IN>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		if (length($fnam) > $cf{file_max}) { $fnam = substr($fnam,0,$cf{file_max}) . '..'; }
		$fnam{$no} = "$fnam.$ex";
	}
	close(IN);
	
	# 画面表示
	header("DLログ閲覧");
	back_btn();
	print <<EOM;
<div id="ttl">■ DLログ閲覧</div>
<table class="form-tbl">
<tr>
	<th>内容</th>
	<th>日時</th>
	<th>ファイル</th>
	<th>ホスト情報</th>
</tr>
EOM

	my %job = (dl => 'DL成功', err => '認証ミス');
	open(IN,"$cf{datadir}/dllog.cgi") or error("open err: dllog.cgi");
	while (<IN>) {
		my ($job,$num,$date,$host) = split(/<>/);
		
		print qq|<tr><td class="ta-c">$job{$job}</td>|;
		print qq|<td>$date</td>|;
		print qq|<td class="grn">$fnam{$num}</td>|;
		print qq|<td>$host</td></tr>\n|;
	}
	close(IN);
	
	print <<EOM;
</table>
EOM
	footer();
}

#-----------------------------------------------------------
#  ファイル名変更
#-----------------------------------------------------------
sub file_rename {
	# 対象ファイル
	my %ren;
	for ( $cgi->param('no') ) { $ren{$_}++; }
	
	# データ更新
	my ($i,@log);
	open(DAT,"+< $cf{datadir}/log.cgi") or error("open err: log.cgi");
	eval "flock(DAT,2);";
	while (<DAT>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		if (defined $ren{$no}) {
			# 乱数作成
			my $new = make_rand();
			
			# リネーム
			rename("$cf{upldir}/$rand/$fnam.$ex","$cf{upldir}/$new/$fnam.$ex");
			
			# フォーマット
			$i++;
			$_ = "$no<>$date<>$mime<>$ex<>$new<>$com<>$del<>$lock<>$size<>$host<>$fnam<>\n";
		}
		push(@log,$_);
	}
	seek(DAT,0,0);
	print DAT @log;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# 完了
	message("$i個のファイルパス名を変更しました");
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my ($ttl,$js) = @_;
	
	print <<EOM;
Content-type: text/html; charset=utf-8

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<link href="$cf{cmnurl}/admin.css" rel="stylesheet">
EOM

	js_boxchk() if ($js eq 'js');
	
	print <<EOM;
<title>$ttl</title>
</head>
<body>
<div id="head"><img src="$cf{cmnurl}/star.png" alt="star" class="icon"> UPLOADER 管理画面 :: </div>
EOM
}

#-----------------------------------------------------------
#  javascriptチェック
#-----------------------------------------------------------
sub js_boxchk {
	print <<'EOM';
<script>
function allcheck() {
	var check = document.getElementsByName('no');
	
    var cnt = check.length;
	for ( var i = 0; i < cnt; i++ ) {
		if (check.item(i).checked) {
			check.item(i).checked = false;
		} else {
			check.item(i).checked = true;
		}
	}
}
</script>
EOM
}

#-----------------------------------------------------------
#  エラー
#-----------------------------------------------------------
sub error {
	my $msg = shift;
	
	header("ERROR!");
	print <<EOM;
<div class="ta-c">
<hr width="350">
<h3>ERROR!</h3>
<p class="err">$msg</p>
<hr width="350">
<p><input type="button" value="前画面に戻る" onclick="history.back()"></p>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my $msg = shift;
	
	header("完了");
	print <<EOM;
<div class="ta-c" style="margin-top:3em;">
<hr width="350">
<p class="msg">$msg</p>
<hr width="350">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<input type="submit" value="管理画面に戻る">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	print <<EOM;
<div class="foot">
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  戻りボタン
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;
	
	print <<EOM;
<div class="back-btn">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; 前画面">| : "" ]}
<input type="submit" value="▲メニュー">
</form>
</div>
EOM
}

