# -*- coding: utf8 -*-

import time
import hashlib
import hmac
import requests
import json
import os

#apikey and secretkey settings
Binance_apikey = os.environ['Binance_apikey']
Binance_secretkey = os.environ['Binance_secretkey']
OKEX_apikey = os.environ['OKEX_apikey']
OKEX_secretkey = os.environ['OKEX_secretkey']
BitMEX_apikey = os.environ['BitMEX_apikey']
BitMEX_secretkey = os.environ['BitMEX_secretkey']
BitMEX2_apikey = os.environ['BitMEX2_apikey']
BitMEX2_secretkey = os.environ['BitMEX2_secretkey']
Bibox_apikey = os.environ['Bibox_apikey']
Bibox_secretkey = os.environ['Bibox_secretkey']
IDEX_wallet = os.environ['IDEX_wallet']

Binance_flag=1
OKEX_flag=1
BitMEX_flag=1
Bibox_flag=1
IDEX_flag=1
sum_flag = Binance_flag+OKEX_flag+BitMEX_flag+Bibox_flag+IDEX_flag

Balance_array = ['','',0,0,0]*999
CoinPrice_array = ['',0]*9999
ETHPrice = 0

j=0
for i in range(0,99):
    url = "https://api.coinmarketcap.com/v2/ticker/?start=" + str(1+i*100) + "&limit=100"
    CoinPrice_response = json.loads(requests.get(url).text)["data"]
    try:
        if len(CoinPrice_response) == 0 :
            break
    except:
        break
    for key in CoinPrice_response:
        symbol = CoinPrice_response[key]["symbol"]
        bal = CoinPrice_response[key]["quotes"]["USD"]["price"]
        CoinPrice_array[j] = [symbol, bal]
        if symbol == "ETH": ETHPrice = bal
        j=j+1
CoinPrice_num = j
CoinPrice_array = CoinPrice_array[0:CoinPrice_num]


def create_sha256_signature(secret, message):
    bsecret = bytes(secret , 'utf8')
    bmessage = bytes(message , 'utf8') 
    return hmac.new(bsecret, bmessage, hashlib.sha256).hexdigest()

# Binance
if Binance_flag==1:
    Binance_headers = {'X-MBX-APIKEY': str(Binance_apikey)}
    Binance_currentTime = str(int(time.time()*1000))
    Binance_params = "timestamp=" + Binance_currentTime
    Binance_params = {'timestamp': str(Binance_currentTime), 'signature':create_sha256_signature(Binance_secretkey,Binance_params)}
    Binance_response = requests.get("https://api.Binance.com/api/v3/account", params=Binance_params, headers=Binance_headers)
    Binance_balance = json.loads(Binance_response.text)['balances']
    j = 0
    for i in range(0,len(Binance_balance)-1):
        bal = float(Binance_balance[i]['free'])
        bal = bal + float(Binance_balance[i]['locked'])
        if bal > 0:
            symbol = Binance_balance[i]['asset']
            for k in range(0,CoinPrice_num):
                if CoinPrice_array[k][0] == symbol:
                    price = CoinPrice_array[k][1]
                    usdvalue = price * bal
                    break
            Balance_array[j] = ['Binance',symbol, bal, price, usdvalue]
            j=j+1

# OKEX
def buildMySignOKEX(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    return hashlib.md5((sign+'secret_key='+secretKey).encode("utf8")).hexdigest().upper()

if OKEX_flag==1:
    OKEX_params = {'api_key': str(OKEX_apikey)}
    OKEX_params = {'api_key': str(OKEX_apikey), 'sign': str(buildMySignOKEX(OKEX_params, OKEX_secretkey))}
    OKEX_response = requests.post("https://www.okex.com/api/v1/userinfo.do", data=OKEX_params)
    OKEX2_response = requests.post("https://www.okex.com/api/v1/wallet_info.do", data=OKEX_params)
    OKEX_balance_borrow = json.loads(OKEX_response.text)['info']['funds']['borrow']
    OKEX_balance_free = json.loads(OKEX_response.text)['info']['funds']['free']
    OKEX_balance_freezed = json.loads(OKEX_response.text)['info']['funds']['freezed']
    OKEX2_balance_holds = json.loads(OKEX2_response.text)['info']['funds']['holds']
    OKEX2_balance_free = json.loads(OKEX2_response.text)['info']['funds']['free']

    for key in OKEX_balance_borrow:
        bal = float(OKEX_balance_borrow[key]) + float(OKEX_balance_free[key]) + float(OKEX_balance_freezed[key]) 
        try:
            bal = bal + float(OKEX2_balance_free[key]) + float(OKEX2_balance_holds[key])
        except:
            pass
        if bal > 0:
            symbol = key.upper()
            for k in range(0,CoinPrice_num):
                if CoinPrice_array[k][0] == symbol:
                    price = CoinPrice_array[k][1]
                    usdvalue = price * bal
                    break
            Balance_array[j] = ['OKEX',symbol, bal, price, usdvalue]
            j=j+1

# BitMEX
if BitMEX_flag==1:
    BitMEX_url = "https://www.BitMEX.com/api/v1/user/margin"
    BitMEX_verb = "GET"
    BitMEX_path = "/api/v1/user/margin"
    BitMEX_expires = str(int(time.time())+5)
    BitMEX_data = ""
    BitMEX_signature = create_sha256_signature(BitMEX_secretkey, BitMEX_verb + BitMEX_path + BitMEX_expires + BitMEX_data)
    BitMEX_headers = {'api-expires':str(BitMEX_expires), 'api-key':str(BitMEX_apikey), 'api-signature':BitMEX_signature}
    BitMEX_response = requests.get(BitMEX_url, headers=BitMEX_headers)
    symbol = "BTC"
    bal1 = float(json.loads(BitMEX_response.text)['marginBalance']) 
    BitMEX2_url = "https://www.BitMEX.com/api/v1/user/margin"
    BitMEX2_verb = "GET"
    BitMEX2_path = "/api/v1/user/margin"
    BitMEX2_expires = str(int(time.time())+5)
    BitMEX2_data = ""
    BitMEX2_signature = create_sha256_signature(BitMEX2_secretkey, BitMEX2_verb + BitMEX2_path + BitMEX2_expires + BitMEX2_data)
    BitMEX2_headers = {'api-expires':str(BitMEX2_expires), 'api-key':str(BitMEX2_apikey), 'api-signature':BitMEX2_signature}
    BitMEX2_response = requests.get(BitMEX2_url, headers=BitMEX2_headers)
    bal2 = float(json.loads(BitMEX2_response.text)['marginBalance'])
    bal = (bal1 + bal2) / 100000000
    for k in range(0,CoinPrice_num):
        if CoinPrice_array[k][0] == symbol:
            price = CoinPrice_array[k][1]
            usdvalue = price * bal
            break
    Balance_array[j] = ['BitMEX',symbol, bal, price, usdvalue]
    j=j+1

# Bibox
def create_md5_signature(secret, message):
    bsecret = bytes(secret , 'utf8')
    bmessage = bytes(message , 'utf8') 
    return hmac.new(bsecret, bmessage, hashlib.md5).hexdigest()
if Bibox_flag==1: 
    Bibox_cmds = '[{"cmd":"transfer/coinList", "body":{}}]'
    Bibox_sign  = create_md5_signature(Bibox_secretkey, Bibox_cmds)
    Bibox_params = {"cmds": Bibox_cmds,"apikey":Bibox_apikey,"sign":Bibox_sign}
    Bibox_response = requests.post("https://api.bibox.com/v1/transfer", data=Bibox_params)
    Bibox_balance = json.loads(Bibox_response.text)
    for i in range(0,999):
        try:
            bal = float(Bibox_balance['result'][0]['result'][i]['totalBalance'])
            if bal > 0:
                symbol = Bibox_balance['result'][0]['result'][i]['symbol']
                for k in range(0,CoinPrice_num):
                    if CoinPrice_array[k][0] == symbol:
                        price = CoinPrice_array[k][1]
                        usdvalue = price * bal
                        break
                Balance_array[j] = ['Bibox',symbol, bal, price, usdvalue]
                j=j+1
        except:
            break

# IDEX
if IDEX_flag==1:
    IDEX_params = {"address" : str(IDEX_wallet)}
    IDEX_response = requests.post("https://api.idex.market/returnCompleteBalances", json=IDEX_params)
    IDEX_balance = json.loads(IDEX_response.text)
    for key in IDEX_balance:
        bal = float(IDEX_balance[key]["available"]) + float(IDEX_balance[key]["onOrders"])
        symbol = key
        for k in range(0,CoinPrice_num):
            if CoinPrice_array[k][0] == symbol:
                price = CoinPrice_array[k][1]
                usdvalue = price * bal
                break
        Balance_array[j] = ['IDEX',symbol, bal, price, usdvalue]
        j=j+1

if sum_flag>0:
    Balance_num = j
    Balance_array = Balance_array[0:Balance_num]
    print(Balance_array)

    sum_usdvalue=0
    for i in range(0,len(Balance_array)):
        sum_usdvalue = sum_usdvalue+Balance_array[i][4]
        
print(sum_usdvalue / ETHPrice)
