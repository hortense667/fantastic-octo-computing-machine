# coding: utf-8
# by Satoshi Endo @hortense667
#フォントデータ（フォントパターン　■と_でできてる）を16進化する
# 縦は8ドットまで、横は128ドットまでの文字をbdf化
# 文字は ★A とか表現する。
# BDFファイルを作るための下処理 入力は _after_burner.txt
# python _punchbdf0x.py _after_burner.txt で実行
import sys
import io
import codecs
import re
import serial
import struct

global fdic
global fmap
global ntbl

ntbl = [" "] * 9	# 漢字フォント読み出し字の保存テーブル
fdic = {}	# フォントテーブルへの辞書

# アタリフォント（一部オリジナル）のフォントテーブル
fmap = []

# COMに１文字送る
def sendptn(ptn):
	if testf != "1":
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
filename = sys.argv[1]
datafile = codecs.open(filename, 'r' , 'utf-8'.lower())
bitmap_f = 0
firstf = 1
print('CHARSET_ENCODING "1"')
for line in datafile:
	line = line.rstrip()
	if '★' in line:
		if firstf == 0:
			print('ENDCHAR')
		firstf = 0
		s = line.replace('★', '')
		bdf_f = 0
		if s == " " or s == "":
			print('STARTCHAR '+ " ")
			print('ENCODING ' + str(ord(" ")))
		else:
			print('STARTCHAR '+ s)
			print('ENCODING ' + str(ord(s)))
		bitmap_f = 1
		kidx = 0
	elif '▲' in line:
		print(line)
	else:
		fontw = len(line)
		line = line.replace('■', '1')
		y = line.replace('＿', '0')
		if len(y) < 8:
			while len(y) < 8:	#左に0をパディング
				y = y + '0'
		elif len(y) > 8:
			while len(y) < 16:	#左に0をパディング
				y = y + '0'
		x = int(y, 2)	#2進法として整数化
		z = hex(x)[2:]	#16進表現に変換
		if (len(z) < 2):
			while len(z) < 2:	#左に0をパディング
				z = '0' + z
		elif (len(z) > 2):
			while len(z) < 4:	#左に0をパディング
				z = '0' + z
		if bdf_f == 0:
			bdf_f = 1
			print('BBX '+str(fontw)+' 8 0 -1')
			print('BITMAP')
		print(z)
print('ENDCHAR')
datafile.close()

