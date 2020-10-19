# coding: utf-8
# by Satoshi Endo @hortense667
# 2020/10/16
# 紙テープ読取／鑽孔機（RS-232C）に文字を花文字で印刷するためのソフト
# パラメーター1：漢字フォントbdfファイル（elisau10.bdfなど）
# バラメーター2：英数字フォントbdfファイル（CHARSET_ENCODING "1"を想定）
# 鑽孔機につないだときは「###### 鑽孔機あるときコメント外す」の行の行頭の#削除
# 鑽孔機つないだときはデバイスマネージャより「COM5」など調べて与える
# 実行するディレクトリに「JIS0208.txt」と使用するbdfファイルを置いておきます。
import sys
import codecs
import re
import serial

global cdic
global fdic
global fmap
global mtbl
global fidx
global plus1line

cdic = {}				# コード変換辞書 JIS －＞ Unicode
fdic = {}				# フォント辞書　フォント情報のトップのテーブル
fmap = []				# フォント情報を展開して持つテーブル
fidx = 0				# fmapのインデックス
mtbl =  [[0] * 16 for i in range(16)]	# パターンの回転用テーブル

###### JIS からUnicodeを求めるためのテーブル生成
def kanjicode_proc(jis0208_filename):
	codefile = codecs.open(jis0208_filename, 'r')
	for line in codefile:
		line = line.rstrip()
		if not re.match('^#', line):
			codes = line.split('\t')
			jiscode = codes[1][2:]
			unicode = codes[2][2:]
			cdic[str(int(jiscode, 16))] = str(int(unicode, 16))	#JISでUnicode求める
	return()

###### COMに１文字送る
def sendptn(ptn):
	while True:
		if ser.out_waiting == 0:
			break
	a = struct.pack( "B", ptn )
	ser.write(a)
	ser.flush()
	return()

###### 画面にパンチするのと同じパターンを表示
def printptn(ptn):
	y = bin(ptn)[2:]			#パンチしたい01パターンを整数化した値がptn
	while len(y) < 8:			#なので再度01パターンに戻してやる
		y = '0' + y			
	z = ''					
	for j in range(8):			#裏返してやる
		z = y[j:j+1] + z		
	z = z.replace('0','＿')			
	y = z.replace('1','■')			
	print(y)				#プリント出力する、シミュレーションですね
	return()

###### １文字のパターンを取り出してCOMに渡す
def fontconv(fontset, moji):
	moji_val = fontset+'_'+str(ord(moji))	#フォント情報の先頭を求める
	if moji_val in fdic:
		mojix = fdic[moji_val]		
		mojihaba = fmap[mojix][0]  + 1	#フォントの横幅
		for i in range(1, mojihaba):		#1列ずとりだしてパンチ
			mojiptn = fmap[mojix][i]	#
#			sendptn(mojiptn)	###### 鑽孔機あるときコメント外す
			printptn(mojiptn)		#画面表示
	return()

###### bdfファイルを読み込んでフォント情報のテーブルに展開する
def readbdf(filename):
	global fidx
	datafile = codecs.open(filename, 'r' , 'utf-8'.lower())
	bitmap_f = 0
	for line in datafile:
		line = line.rstrip()
		if re.match('^CHARSET_ENCODING', line):
			chrencoding = line.replace('CHARSET_ENCODING ', '')
		elif re.match('^ENCODING ', line):	#文字コードをフォント辞書に登録
			encoding = line.replace('ENCODING ', '')
			if chrencoding == '"0"':	#JISコードのときUnicodeに変換
				encoding = cdic[encoding]
			if (int(encoding)) > 255:	#2バイト（漢字）か1バイトかで辞書を振り分ける
				fdic['k_'+encoding] = fidx	#2バイト（漢字のとき）
			else:
				fdic['1_'+encoding] = fidx	#1バイトのとき
			bitmap_f = 0
		elif 'BBX' in line:			#フォントの幅と高さの処理
			fontwidth = int(line[4:6])
			fonthight = int(line[6:8]) 
			fmap.append([fontwidth])	#フォント情報にフォントの横幅をセット
		elif 'BITMAP' in line:			#フォントピクセルマップ開始
			bitmap_f = 1
			kidx = 0
		elif 'ENDCHAR' in line:
			for j in range(fontwidth):	#テーブルに入れといたピクセルを90度回転
				z = ''			
				for i in range(fonthight):
					z = z + str(mtbl[i][j])
				x = int(z, 2)
				fmap[fidx].append(x)	#フォント情報のテーブルにセット
			bitmap_f = 0
			fidx = fidx + 1
		elif bitmap_f == 1:		#ピクセルを裏返してテーブルにセット
			mojiptn = line
			x = int(mojiptn, 16)	#16進表現をとりこむ
			y = bin(x)[2:]	#それを2進表現に変換
			while len(y) < len(mojiptn) * 4:	#左に0をパディング
				y = '0' + y
			z = ''
			for j in range(len(mojiptn) * 4):	#パターンを裏返しに 
				z = y[j:j+1] + z		#本当はfontwidth
				mtbl[kidx][j] = y[j:j+1]
			kidx = kidx + 1
	datafile.close()
	return()

###### COMポートの準備
def comport_proc(comn):
	if comn == "":
		comn = "COM5"
	ser = serial.Serial(
		port = com_no,
		baudrate = 300,
		)

#==========================================
# メイン処理
#==========================================
###### Shift-JIS JIS Unicode 変換テーブル作成
kanjicode_proc("JIS0208.txt")

###### フォントファイルの読み込みとテーブルへの展開
readbdf(sys.argv[1])	#漢字bdfファイル読み込み

readbdf(sys.argv[2])	#英数bdfファイル読み込み

###### COMポートの処理
com_no = input("COMポートを指定してください (デバイスマネージャを参照 / ex. COM5 ) : ")
#comport_proc(com_no)		###### 鑽孔機あるときコメント外す

###### 印刷したい文字列を受け取りパンチする
while True:
	mojistr = input("印刷したい文字列を入力してください（入力ナシで終了） : ")
	if mojistr == "":
		break
	for j in range(len(mojistr)):
		c = mojistr[j :j + 1]
		if c != "":
			if ord(c) > 255:
				fontconv('k', c)	#2バイト（漢字）コードのとき
			else:
				fontconv('1', c)	#1バイトコードのとき
