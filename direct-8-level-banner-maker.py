# coding: utf-8
# by Satoshi Endo @hortense667
# フォントデータ（フォントパターン　■と_でできてる）をそのまま印刷する
# ★を含む行は印刷しない。
# １フォントは縦に８ドットしか対応しない
# 横は1024ドットまで
# 紙テープ読取／鑽孔機（RS-232C）に文字を花文字で印刷するためのソフトです。
import sys
import io
import codecs
import re
import serial
import struct

global fmap
global mtbl
global ntbl

mtbl =  [[0] * 1024 for i in range(1024)]	# パターンの回転用テーブル（リストの初期化こうやる）
ntbl = [" "] * 9			# フォント読み出し字の保存テーブル

# COMに１文字送る
def sendptn(ptn):
	if testf != "t":
		while True:
			if ser.out_waiting == 0:
				break
		a = struct.pack( "B", ptn )
		ser.write(a)
		ser.flush()
	y = bin(ptn)[2:]			#for test
	while len(y) < 8:			#for test
		y = '0' + y			#for test
	z = ''					#for test
	for j in range(8):			#パターンを裏返しに
		z = y[j:j+1] + z		#for test
	z = z.replace('0','＿')			#for test
	y = z.replace('1','■')			#for test
	print(y)				#for test
	return()

#==========================================
# ここからメイン処理
#==========================================
#標準出力のおまじない
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp932'.lower())
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'.lower())


#フォントファイルの読み込みとテーブルへの展開
numfont = len(sys.argv) - 2
testf = sys.argv[1] 			# 鑽孔機接続してないとき"t"そうでないとき“p”

# COMポートの処理
if testf != "t":
	com_no = input("COMポートを指定してください (デバイスマネージャを参照 / ex. COM3 ) : ")
	if com_no == "":
		com_no = "COM3"


if testf != "t":
	ser = serial.Serial(
	port = com_no,
	baudrate = 300,
	)
	
fontno = 0
kidx = 0

for n in range(numfont):
	filename = sys.argv[n+2] 
	datafile = codecs.open(filename, 'r' , 'utf-8'.lower())
	bitmap_f = 0
	for line in datafile:
		line = line.rstrip()
		if '★' in line:
			bitmap_f = 1
			kidx = 0
		else:
			line = line.replace('■', '1')
			mojiptn = line.replace('＿', '0')
			ntbl[kidx] = mojiptn
			kidx = kidx + 1
			if kidx == 8:		#8列分読んだらパターンを反転回転する（8以上は落ちる）
				for i in range(8):
					y = ntbl[i]
					z = ''
					for j in range(len(y)):	#パターンを裏返しに 
						z = y[j:j+1] + z		#本当はfontwidth
						mtbl[i][j] = y[j:j+1]
				for j in range(len(y)):		#パターンを90度回転して
					z = ''			
					for i in range(8):
						z = z + str(mtbl[i][j])
					x = int(z, 2)
					sendptn(x)
	if testf != "t":
		for i in range(12):
			sendptn(0)
	datafile.close()
	fontno = fontno + 1

