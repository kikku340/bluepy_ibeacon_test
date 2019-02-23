#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######Imports#####
from bluepy import btle
from datetime import datetime
import struct
import binascii
import csv
import os

#####Defines###### 
IBEACON_ADTYPE = 0x4c00
IBEACON_COMPANYID = 0x0215
SAVECSVPASS = './ibeaconlog.csv'
SCAN_LATENCY = 0.5
BLE_DEVICE_NO = 0
LOGGING = True

def writeCSV(uuid, major, minor, txpower):
	#UUIDだけ何故かbyte型なのでstr型に変換（なんで...）
	uuid_str = str(binascii.b2a_hex(uuid), 'utf-8')
	date_n = datetime.now().strftime("%Y/%m/%d")
	time_n = datetime.now().strftime("%H:%M:%S")
	
	wlist = [date_n, time_n, uuid_str, major, minor, txpower]
	indexlist = ['date', 'time', 'uuid', 'major', 'minor', 'txpower']
	# ファイルがない場合、作成と１行目にインデックスを書き込む
	if (os.path.isfile(SAVECSVPASS) == False):
		with open(SAVECSVPASS, 'w') as f:
			writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
			writer.writerow(indexlist)

	# 受信データの書き込み
	with open(SAVECSVPASS, 'a') as f:
		writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
		writer.writerow(wlist)


if __name__ == '__main__':
	scanner = btle.Scanner(BLE_DEVICE_NO)
	while True:
		# 周辺デバイスのスキャン(devicesは受信した各データが格納される)
		devices = scanner.scan(SCAN_LATENCY)

		for device in devices:
			for (adTypeCode, description, valueText) in device.getScanData():
				if (description == "Manufacturer"):
					# アドバタイズデータをbyte形式に変換
					adv_hex = binascii.unhexlify(valueText)
					# iBeaconと判定できるデータだけ抽出
					ADType, CompanyID = struct.unpack('>HH', adv_hex[:4])
					# 受信したのはiBeacon？
					if (ADType == IBEACON_ADTYPE) and (CompanyID == IBEACON_COMPANYID):
						# iBeaconないの各データを抽出、表示する
						UUID, Major, Minor, TXPower = struct.unpack('>16sHHb', adv_hex[4:25])
						print(f"ibeadon detected!\r\ndeviceID:{device.addr}")
						print(f"\tUUID:{str(binascii.b2a_hex(UUID), 'utf-8')}")
						print(f"\tMajor:{Major}")
						print(f"\tMinor:{Minor}")
						print(f"\tTXPower:{TXPower}")
						if (LOGGING == True):
							writeCSV(UUID, Major, Minor, TXPower)