#!/usr/local/bin/perl

#┌─────────────────────────────
#│ File Uploder : upload.cgi - 2019/12/22
#│ copyright (c) kentweb, 1997-2019
#│ https://www.kent-web.com/
#└─────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;

# 設定内容認識
require "./init.cgi";
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
error('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# 条件分岐
if ($in{get}) { download(); }
if ($in{del}) { del_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'upld') { upld_file(); }
list_data();

#-----------------------------------------------------------
#  一覧リスト
#-----------------------------------------------------------
sub list_data {
	# ページ数定義
	my $pg = $in{pg} || 0;
	
	# UTF-8定義
	my $byte1 = '[\x00-\x7f]';
	my $byte2 = '[\xC0-\xDF][\x80-\xBF]';
	my $byte3 = '[\xE0-\xEF][\x80-\xBF]{2}';
	my $byte4 = '[\xF0-\xF7][\x80-\xBF]{3}';
	
	# キーワード配列化
	$in{q} =~ s/　/ /g;
	my @q = split(/\s+/,$in{q});
	
	# ログファイル読込
	my ($i,@data,%ct);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	while(<IN>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		# --- 検索
		if ($in{q} ne '') {
			my $flg;
			for my $q (@q) {
				if ("$fnam $com" =~ /^(?:$byte1|$byte2|$byte3|$byte4)*?\Q$q\E/i) {
					$flg++;
				} else {
					$flg = 0;
					last;
				}
			}
			next if (!$flg);
		}
		
		$i++;
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{pg_max});
		
		$ct{$no} = 0;
		push(@data,$_);
	}
	close(IN);
	
	# 繰越ボタン作成
	my $pg_btn = make_pgbtn($i,$pg);
	
	# カウントファイル読込
	open(IN,"$cf{datadir}/count.dat") or error("open err: count.dat");
	while(<IN>) {
		chomp;
		my ($no,$cnt) = split(/:/);
		
		if (defined $ct{$no}) { $ct{$no} = $cnt; }
	}
	close(IN);
	
	# 許可拡張子（表示用）
	my $ext = ext_file();
	
	# テンプレート読込
	my $file = $in{mode} eq 'find' ? 'find.html' : 'upload.html';
	open(IN,"$cf{tmpldir}/$file") or error("open err: $file");
	my $tmpl = join('',<IN>);
	close(IN);
	
	# 文字置換
	$tmpl =~ s/!(homepage|html_title|maxcom|cmnurl|max_com)!/$cf{$1}/g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!ext!/$ext/g;
	$tmpl =~ s|!page_btn!|<div class="pgbtn">$pg_btn</div>|g;
	$tmpl =~ s/!q!/$in{q}/g;
	$tmpl =~ s|!maxdata!|int($cf{maxdata}/1024) . 'KB'|e;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	
	if ($in{q} ne '') {
		$tmpl =~ s/!result!/$i/g;
		$tmpl =~ s|<!-- upform -->.+?<!-- /upform -->||s;
	} else {
		$tmpl =~ s|<!-- find_result -->.+?<!-- /find_result -->||s;
	}
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# ヘッダー部展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# ループ部展開
	foreach (@data) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnm) = split(/<>/);
		
		# ファイル名カット
		if (length($fnm) > $cf{file_max}) { $fnm = substr($fnm,0,$cf{file_max}) . '..'; }
		
		# アイコン：lock or free
		my ($icon,$fnam);
		if ($lock) {
			$icon = 'lock.png';
			$fnam = qq|<a href="$cf{upload_cgi}?get=$no" target="popup" onclick="popup('$cf{upload_cgi}?get=$no')">$fnm.$ex</a>|;
		} elsif ($mime =~ /^image/i) {
			$icon = 'image.png';
			$fnam = qq|<a href="$cf{upload_cgi}?get=$no" target="_blank">$fnm.$ex</a>|;
		} else {
			$icon = 'put.png';
			$fnam = qq|<a href="$cf{upload_cgi}?get=$no" target="_blank">$fnm.$ex</a>|;
		}
		
		# mime情報カット
		if (length($mime) > $cf{mime_max}) {
			$mime = substr($mime,0,$cf{mime_max}) . '..';
		}
		
		# 文字置換
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!size!/$size/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s|!icon!|<img src="$cf{cmnurl}/$icon" alt="" class="icon">|g;
		$tmp =~ s/!fname!/$fnam/g;
		$tmp =~ s/!comment!/$com/g;
		$tmp =~ s/!count!/$ct{$no}/g;
		$tmp =~ s/!mime!/$mime/g;
		$tmp =~ s/!upload_cgi!/$cf{upload_cgi}/g;
#		$tmp =~ s|!ico_del!|<img src="$cf{ico_del}" alt="削除" class="icon">|g;
		print $tmp;
	}
	# データフラッシュ
	@data = (); %ct = ();
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  ファイルアップロード
#-----------------------------------------------------------
sub upld_file {
	# IP/ホストチェック
	my ($host,$addr) = get_host();
	chk_host($host,$addr);
	
	# アップロードファイル取得
	my $upfile = $cgi->param_filename('upfile');
	
	# 入力チェック
	my $err;
	if (!$upfile) { $err .= "ファイルが未入力です<br>\n"; }
	if (!$in{comment}) { $err .= "コメントが未入力です<br>\n"; }
	elsif (count_str($in{comment}) == 1) { $err .= "コメントは$cf{max_com}文字以内です<br>\n"; }
	error($err) if ($err);
	
	# MIMEタイプ取得
	my $mime = $cgi->param_mime('upfile');
	
	# オリジナルファイル名取得
	my ($fnam,$ext) = $upfile =~ /([^:\/\\]+)\.(\w+)$/
				? ($1,$2)
				: error("アップファイル名が不正です");
	$ext =~ tr/A-Z/a-z/;
	
	# 拡張子チェック
	check_upl($mime,$ext);
	
	# mimeのHTML無効化
	$mime = $cgi->htmlize($mime);
	
	# 乱数発生
	my $rand = make_rand();
	
	# 削除キー/暗証キーを暗号化
	my $delkey = encrypt($in{delkey}) if ($in{delkey});
	my $pwdkey = encrypt($in{pwdkey}) if ($in{pwdkey});
	
	# 日付取得
	my $date = get_date();
	
	# ログオープン
	my ($i,@log,%del);
	open(DAT,"+< $cf{datadir}/log.cgi") or error("open err: log.cgi");
	eval "flock(DAT,2);";
	while(<DAT>) {
		$i++;
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		if ($i <= $cf{log_max} - 1) {
			push(@log,$_);
		} else {
			$del{$no}++;
			unlink("$cf{upldir}/$rand/$no.$ex");
		}
	}
	
	# 採番
	my ($no) = (split(/<>/,$log[0]))[0];
	$no = sprintf("%05d",$no+1);
	
	# アップロード
	mkdir("$cf{upldir}/$rand",0777) or error("mkdir err: $cf{upldir}/$rand");
	
	# ファイル名定義
	if ($fnam =~ /[^\w\-]/) { $fnam = $no; }
	my $size = upload_file($upfile,"$rand/$fnam.$ext");
	
	# ログ更新
	unshift(@log,"$no<>$date<>$mime<>$ext<>$rand<>$in{comment}<>$delkey<>$pwdkey<>$size<>$host<>$fnam<>\n");
	seek(DAT,0,0);
	print DAT @log;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# カウントファイルに追加
	my @log;
	open(DAT,"+< $cf{datadir}/count.dat") or error("write err: count.dat");
	eval "flock(DAT,2);";
	while(<DAT>) {
		my ($no,$cnt) = split(/:/);
		next if (defined $del{$no});
		
		push(@log,$_);
	}
	unshift(@log,"$no:0\n");
	seek(DAT,0,0);
	print DAT @log;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# 完了メッセージ
	message("アップロードを完了しました");
}

#-----------------------------------------------------------
#  アップロード
#-----------------------------------------------------------
sub upload_file {
	my ($upfile,$upname) = @_;
	
	# アップファイル定義
	$upname = "$cf{upldir}/$upname";
	
	open(UP,"+> $upname") or error("up err: $upname");
	binmode(UP);
	print UP $in{upfile};
	close(UP);
	
	# パーミッションを666に
	chmod(0666,$upname);
	
	# 容量取得
	my $size = -s $upname;
	if ($size >= 1024) {
		$size = int($size/1024) . 'KB';
	} else {
		$size .= 'B';
	}
	return $size;
}

#-----------------------------------------------------------
#  ダウンロード
#-----------------------------------------------------------
sub download {
	# 引数チェック
	if ($in{get} =~ /\D/) { error("不正な値です"); }
	if ($in{pwdkey} && $in{key} eq '') { error("暗証キーが未入力です"); }
	
	# ログファイル読込
	my ($file,$pwflg,$ctype);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	while(<IN>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
		
		# 該当データ
		if ($in{get} == $no) {
			$file  = "$rand/$fnam.$ex";
			$pwflg = $lock;
			$ctype = $mime;
			last;
		}
	}
	close(IN);
	
	# 該当なし
	if (!$file) { error("該当のファイルはありません"); }
	
	# 暗証キー設定のとき
	if ($pwflg) {
		
		# 暗証入力時
		if ($in{pwdkey}) {
			if (decrypt($in{key},$pwflg) != 1) {
				save_log('err');
				error("認証できません");
			}
		
		# パスワード画面
		} else {
			pwd_form();
		}
	}
	
	# カウントアップ更新
	my @data;
	open(DAT,"+< $cf{datadir}/count.dat") or error("open err: count.dat");
	eval "flock(DAT,2);";
	while(<DAT>) {
		my ($no,$cnt) = split(/:/);
		
		if ($in{get} == $no) {
			chomp($cnt);
			$cnt++;
			$_ = "$no:$cnt\n";
		}
		push(@data,$_);
	}
	seek(DAT,0,0);
	print DAT @data;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# ログ記録
	save_log('dl');
	
	# 画像のときはリンク画面表記
	if ($ctype =~ /^image/) {
		img_page($file);
	
	# 画像以外はリダイレクト
	} else {
		if ($ENV{PERLXS} eq "PerlIS") {
			print "HTTP/1.0 302 Temporary Redirection\r\n";
			print "Content-type: text/html\n";
		}
		print "Location: $cf{uplurl}/$file\n\n";
		exit;
	}
}

#-----------------------------------------------------------
#  データ削除
#-----------------------------------------------------------
sub del_data {
	$in{del} =~ s/\D//g;
	
	# 削除実行
	if ($in{key} ne "" && $in{delkey} == 1) {
		
		my ($dfile,$drand,$crypt,@data);
		open(DAT,"+< $cf{datadir}/log.cgi") or error("open err: log.cgi");
		eval "flock(DAT,2);";
		while(<DAT>) {
			my ($no,$date,$fnam,$ex,$rand,$com,$del,$lock,$size,$host,$fnam) = split(/<>/);
			
			if ($in{del} == $no) {
				$dfile = "$fnam.$ex";
				$drand = $rand;
				$crypt = $del;
				next;
			}
			push(@data,$_);
		}
		# 削除キーなし
		if (!$crypt) {
			close(DAT);
			error("削除キーが未設定です");
		}
		# 照合
		if (decrypt($in{key},$crypt) != 1) {
			close(DAT);
			error("認証できません");
		}
		# 更新
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# 添付削除
		unlink("$cf{upldir}/$drand/$dfile");
		rmdir("$cf{upldir}/$drand");
		
		# カウントファイル削除
		my ($file,$crypt,@data);
		open(DAT,"+< $cf{datadir}/count.dat") or error("open err: count.dat");
		eval "flock(DAT,2);";
		while(<DAT>) {
			my ($no,$cnt) = split(/:/);
			next if ($in{del} == $no);
			push(@data,$_);
		}
		# 更新
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# 完了
		message("削除を完了しました");
	
	# 入力フォーム
	} else {
		del_form();
	}
}

#-----------------------------------------------------------
#  日付取得
#-----------------------------------------------------------
sub get_date {
	my ($min,$hour,$day,$mon,$year) = (localtime(time))[1..5];
	
	sprintf("%04d/%02d/%02d-%02d:%02d", $year+1900,$mon+1,$day,$hour,$min);
}

#-----------------------------------------------------------
#  利用規約
#-----------------------------------------------------------
sub note_page {
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!(upload_cgi|html_title|cmnurl|log_max)!/$cf{$1}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s|!maxdata!|int($cf{maxdata}/1024) . 'KB'|e;
	$tmpl =~ s/!ext!/ext_file()/e;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my $msg = shift;
	
	open(IN,"$cf{tmpldir}/mesg.html") or error("open err: mesg.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!(upload_cgi|html_title|cmnurl)!/$cf{$1}/g;
	$tmpl =~ s/!message!/$msg/g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub error {
	my $err = shift;
	
	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!error!/$err/g;
	$tmpl =~ s/!(upload_cgi|html_title|cmnurl)!/$cf{$1}/g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;
	
	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="https://www.kent-web.com/" target="_top">UPLOADER</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  crypt暗号
#-----------------------------------------------------------
sub encrypt {
	my $in = shift;
	
	# salt作成
	my @wd = ('a'..'z', 'A'..'Z', 0..9, '.', '/');
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	
	# 暗号化
	crypt($in,$salt) || crypt ($in, '$1$' . $salt);
}

#-----------------------------------------------------------
#  crypt照合
#-----------------------------------------------------------
sub decrypt {
	my ($in,$dec) = @_;
	
	# salt取得
	my $salt = $dec =~ /^\$1\$(.*)\$/ ? $1 : substr($dec, 0, 2);
	
	# 照合
	if (crypt($in,$salt) eq $dec || crypt($in, '$1$' . $salt) eq $dec) {
		return 1;
	} else {
		return 0;
	}
}

#-----------------------------------------------------------
#  ファイルチェック
#-----------------------------------------------------------
sub check_upl {
	my ($mime,$ext) = @_;
	
	my $flg;
	if ($cf{ok_gif}) {
		if ($mime =~ /^image\/gif$/i and $ext eq 'gif') { $flg++; }
	}
	if (!$flg and $cf{ok_jpeg}) {
		if ($mime =~ /^image\/p?jpeg$/i and $ext =~ /^jpe?g$/) { $flg++; }
	}
	if (!$flg and $cf{ok_png}) {
		if ($mime =~ /^image\/png$/i and $ext eq 'png') { $flg++; }
	}
	if (!$flg and $cf{ok_pdf}) {
		if ($mime =~ /^application\/pdf$/i and $ext eq 'pdf') { $flg++; }
	}
	if (!$flg and $cf{ok_zip}) {
		if ($mime =~ /^application\/(x-)?zip(-compressed)?$/i and $ext eq 'zip') { $flg++; }
	}
	if (!$flg and $cf{ok_text}) {
		if ($mime =~ /^text\/plain$/i and $ext =~ /^te?xt$/) { $flg++; }
	}
	if (!$flg and $cf{ok_word}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?word$/i and $ext eq 'doc') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.wordprocessingml\.document$/i and $ext eq 'docx') { $flg++; }
	}
	if (!$flg and $cf{ok_excel}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?excel$/i and $ext eq 'xls') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet$/i and $ext eq 'xlsx') { $flg++; }
	}
	if (!$flg and $cf{ok_ppt}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?powerpoint$/i and $ext eq 'ppt') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.presentationml\.presentation$/i and $ext eq 'pptx') { $flg++; }
	}
	
	if (!$flg) { error('このファイルは取り扱いできません'); }
}

#-----------------------------------------------------------
#  パスワード入力フォーム
#-----------------------------------------------------------
sub pwd_form {
	open(IN,"$cf{tmpldir}/pass.html") or error("open err: pass.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!(upload_cgi|html_title|cmnurl)!/$cf{$1}/g;
	$tmpl =~ s/!num!/$in{get}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  ファイル削除フォーム
#-----------------------------------------------------------
sub del_form {
	# ファイル番チェック
	if ($in{del} !~ /^\d+$/) { error('不正な要求です'); }
	
	# データ検出
	my ($fname,$comm,$upday,$dele);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	while(<IN>) {
		my ($no,$date,$mime,$ex,$rand,$com,$del,$lock,$size,$host) = split(/<>/);
		
		# 該当データ
		if ($in{del} == $no) {
			$fname = "$no.$ex";
			$comm  = $com;
			$upday = $date;
			$dele  = $del;
			last;
		}
	}
	close(IN);
	
	# エラー
	if ($fname eq '') { error('指定ファイルはありません'); }
	elsif ($dele eq '') { error('削除キーが未設定のため削除できません'); }
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/dele.html") or error("open err: dele.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	# 文字置換え
	$tmpl =~ s/!(upload_cgi|html_title|cmnurl)!/$cf{$1}/g;
	$tmpl =~ s/!num!/$in{del}/g;
	$tmpl =~ s/!fname!/$fname/g;
	$tmpl =~ s/!date!/$upday/g;
	$tmpl =~ s/!comment!/$comm/g;
	
	# 画面表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  画像リンクページ
#-----------------------------------------------------------
sub img_page {
	my $file = shift;
	my $ex = $file =~ /\.(\w+)$/ ? $1 : "";
	
	open(IN,"$cf{tmpldir}/image.html") or error("open err: image.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!(cmnurl|html_title)!/$cf{$1}/g;
	$tmpl =~ s|!link!|$cf{uplurl}/$file|g;
	$tmpl =~ s/!fname!/$in{get}.$ex/g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  繰越ボタン作成
#-----------------------------------------------------------
sub make_pgbtn {
	my ($i,$pg) = @_;
	
	# 引数
	my $param;
	if ($in{q} ne '') {
		my $q = $in{q};
		$q =~ s/(\W)/'%'.unpack("H2",$1)/ego;
		$q =~ s/ /+/g;
		
		$param = "&amp;q=$q";
	}
	
	# ページ繰越数定義
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};
	
	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<span class="page active">$x</span>\n!);
			} else {
				push(@pg,qq!<a href="$cf{upload_cgi}?pg=$y$param" class="page gradient">$x</a>\n!);
			}
			$x++;
			$y += $cf{pg_max};
			$z -= $cf{pg_max};
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('', @pg);
	if ($back >= 0) {
		$ret = qq!<a href="$cf{upload_cgi}?pg=$back$param" class="page gradient">&laquo;</a>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<a href="$cf{upload_cgi}?pg=$next$param" class="page gradient">&raquo;</a>\n!;
	}
	return $ret ? qq|<div class="pagination">\n$ret</div>| : '';
}

#-----------------------------------------------------------
#  IP/ホスト取得
#-----------------------------------------------------------
sub get_host {
	# IP/ホスト取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};
	
	# 変換
	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	if ($host eq '') { $host = $addr; }
	return ($host,$addr);
}

#-----------------------------------------------------------
#  アクセス制限
#-----------------------------------------------------------
sub chk_host {
	my ($host,$addr) = @_;
	
	# IPチェック
	my $flg;
	foreach ( split(/\s+/, $cf{deny_addr}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		
		if ($addr =~ /^$_/i) { $flg++; last; }
	}
	if ($flg) { error("アクセスを許可されていません");	}
	
	# ホストチェック
	if ($host ne $addr) {
		my $flg;
		foreach ( split(/\s+/, $cf{deny_host}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;
			if ($host =~ /$_$/i) { $flg++; last; }
		}
		if ($flg) { error("アクセスを許可されていません"); }
	}
}

#-----------------------------------------------------------
#  取り扱いファイル
#-----------------------------------------------------------
sub ext_file {
	my $ext;
	foreach ( keys %cf ) {
		next if ($_ !~ /^ok_(\w+)/);
		my $file = $1;
		next if (!$cf{$_});
		
		$file =~ tr/a-z/A-Z/;
		$ext .= "$file, ";
	}
	$ext =~ s/, $//;
	
	return $ext;
}

#-----------------------------------------------------------
#  ログ保存
#-----------------------------------------------------------
sub save_log {
	my ($job) = @_;
	
	# ホスト取得
	my ($host,$addr) = get_host();
	
	# 日付取得
	my $date = get_date();
	
	my ($i,@log);
	open(DAT,"+< $cf{datadir}/dllog.cgi") or error("write err: dllog.cgi");
	eval "flock(DAT,2);";
	while(<DAT>) {
		$i++;
		push(@log,$_);
		
		last if ($i >= $cf{dllog_max} - 1);
	}
	unshift(@log,"$job<>$in{get}<>$date<>$host<>\n");
	seek(DAT,0,0);
	print DAT @log;
	truncate(DAT,tell(DAT));
	close(DAT);
}

#-----------------------------------------------------------
#  文字カウント
#-----------------------------------------------------------
sub count_str {
	my $str = shift;
	
	my $i = 0;
	my $flg;
	while ($str =~ /([\x00-\x7f]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})/gx) {
		$i++;
		if ($i > $cf{max_com}) {
			$flg = 1;
			last;
		}
	}
	return $flg;
}

