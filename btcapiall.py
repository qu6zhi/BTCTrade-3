import okcoin
from bitf import *
import json
from  datetime  import  *
import time
from huobi import *
from btceapi import *

def get_info_be(btx):
	tick = btx.get_tick()
	info_be = {}
	info_be['price'] = float(tick['ticker']['last'])

	depth_be = btx.get_depth()

	up_amt = info_be['price'] * 1.003
	down_amt = info_be['price'] * 0.997
	
	info_be['buy'] = 0 
	info_be['buynum'] = 0
	for i in range(0,149):
		ask_amt = float(depth_be['asks'][i][0])
		if ask_amt <= up_amt:
			info_be['buy'] = ask_amt
			info_be['buynum'] += float(depth_be['asks'][i][1])
		else:
			break
	
	info_be['sell'] = 0 
	info_be['sellnum'] = 0
	for i in range(0,149):
		bid_amt = float(depth_be['bids'][i][0])
		if bid_amt >= down_amt:
			info_be['sell'] = bid_amt
			info_be['sellnum'] += float(depth_be['bids'][i][1])
		else:
			break

	acc = btx.getInfo()
	info_be['usd'] = float(acc['return']['funds']['usd'])
	info_be['btc'] = float(acc['return']['funds']['btc'])
# be have not frazen usd amount , return open order 
	info_be['f_usd'] = acc['return']['open_orders']
	info_be['f_btc'] = acc['return']['open_orders']
	
	return info_be

def be_sell(bex,be,btc):
	price = be['sell']
	total = price * btc
	strP =  "We are going to sell %f BTC for %f in BE, total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = bex.Trade('btc_usd','sell',price,btc)
	print result

def be_buy(bex,be,btc):
	price = be['buy']
	total = price * btc
	strP =  "We are going to buy %f BTC for %f in BE, total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = bex.Trade('btc_usd','buy',price,btc)
	print result

def get_info_hb(hbx):
	tick = hbx.get_tick()
	info_hb = {}
	info_hb['price'] = float(tick['ticker']['last'])  

	depth_hb = hbx.get_depth()
	
	up_amt = info_hb['price'] * 1.003
	down_amt = info_hb['price'] * 0.997

	info_hb['buy'] = 0
	info_hb['buynum'] = 0
	for i in range(299,1,-1):
		ask_amt = float(depth_hb['asks'][i][0])
		if ask_amt <= up_amt:
			info_hb['buy'] = ask_amt 
        		info_hb['buynum'] += float(depth_hb['asks'][i][1])
		else:
			break

	info_hb['sell'] = 0
	info_hb['sellnum'] = 0
	for i in range(0,299):
		bid_amt = float(depth_hb['bids'][i][0])
		if bid_amt >= down_amt:
			info_hb['sell'] = bid_amt 
        		info_hb['sellnum'] += float(depth_hb['bids'][i][1])
		else:
			break

	acc = hbx.get_account_info()
	info_hb['cny'] = float(acc['available_cny_display'])
	info_hb['btc'] = float(acc['available_btc_display'])
	info_hb['f_cny'] = float(acc['frozen_cny_display'])
	info_hb['f_btc'] = float(acc['frozen_btc_display'])

	return info_hb

def hb_sell(hbx,hb,btc):
	price = hb['sell']
	total = price * btc
	strP =  "We are going to buy %f BTC for %f in HB, total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = hbx.sell(price,btc)
	print result

def hb_buy(hbx,hb,btc):
	price = hb['buy']
	total = price * btc
	strP =  "We are going to buy %f BTC for %f in HB,total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = hbx.buy(price,btc)
	print result

def get_info_ok(authobj):
	m_okcoin = okcoin.MarketData()
	tick_ok = m_okcoin.ticker('btc_cny')
	info_ok = {}
	info_ok['price'] = float(tick_ok.last)

	deph_ok = m_okcoin.get_depth('btc_cny')

	up_amt = info_ok['price'] * 1.003
	down_amt = info_ok['price'] * 0.997

	info_ok['buy'] = 0
	info_ok['buynum'] = 0
	for i in range(199,0,-1):
		ask_amt = float(deph_ok.asks[i][0])
		if ask_amt <= up_amt:
			info_ok['buy'] = ask_amt 
        		info_ok['buynum'] += float(deph_ok.asks[i][1])
		else:
			break
 
        info_ok['sell'] = 0
	info_ok['sellnum'] = 0
	for i in range(0,199):
		bid_amt = float(deph_ok.bids[i][0])
		if bid_amt >= down_amt:
			info_ok['sell'] = bid_amt 
        		info_ok['sellnum'] += float(deph_ok.bids[i][1])
		else:
			break 

	acc =  authobj.get_info()	
	info_ok['cny'] = float(acc['info']['funds']['free']['cny'])
	info_ok['btc'] = float(acc['info']['funds']['free']['btc'])
	info_ok['f_cny'] = float(acc['info']['funds']['freezed']['cny'])
	info_ok['f_btc'] = float(acc['info']['funds']['freezed']['btc'])

	return info_ok

def ok_sell(auth,ok,btc):
	price = ok['sell']
	total = price * btc
	strP =  "We are going to sell %f BTC for %f in OK, total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = auth.trade('btc_cny','sell',price,btc)
	print result
	
def ok_buy(auth,ok,btc):
	price = ok['buy']
	total = price * btc
	strP =  "We are going to buy %f BTC for %f in OK, total is %f" % (btc, price,total)
	print strP
	writefile(strP)

	result = auth.trade('btc_cny','buy',price,btc)
	print result

def get_info_bf(bfx):
	tick_bf = bfx.ticker()
	info_bf = {}
	info_bf['price'] = float(tick_bf['last_price'])

	preload = {}
	preload['symbol'] = 'btcusd'
	deph_bf = bfx.book(preload)

	up_amt = info_bf['price'] * 1.005
	down_amt = info_bf['price'] * 0.995
        
	info_bf['buy'] = 0
	info_bf['buynum'] = 0
	for i in range(0,59):
		ask_amt = float(deph_bf['asks'][i]['price'])
		if ask_amt <= up_amt:
			info_bf['buy'] = ask_amt 
        		info_bf['buynum'] += float(deph_bf['asks'][i]['amount'])
		else:
			break 
        
	info_bf['sell'] = 0
	info_bf['sellnum'] = 0
	for i in range(0,59):
		bid_amt = float(deph_bf['bids'][i]['price']) 
		if bid_amt >= down_amt:
			info_bf['sell'] = bid_amt 
        		info_bf['sellnum'] +=float(deph_bf['bids'][i]['amount'])
		else:
			break 
	
	acc = bfx.balances()
	for item in acc:
		if item['currency'] == 'btc' and item['type'] == 'exchange':
			info_bf['btc'] = float(item['available'])
			info_bf['f_btc'] = float(item['amount']) - info_bf['btc']
		if item['currency'] == 'usd' and item['type'] == 'exchange':
			info_bf['usd'] = float(item['available'])
			info_bf['f_usd'] = float(item['amount']) - info_bf['usd']
	
	return info_bf

def bf_buy(bfx,bf,btc):
	price = bf['buy']
	total = price * btc
	strP =  "We are going to buy %f BTC for %f in BF, total is %f" % (btc, price, total)
	print strP
	writefile(strP)

	payload = {}
	payload['symbol'] = 'btcusd'
	payload['amount'] = str(btc)
	payload['price'] = str(price)
	payload['exchange'] = 'all'
	payload['side'] = 'buy'
	payload['type'] = 'exchange limit'
	border = bfx.order_new(payload)
	print border	

def bf_sell(bfx,bf,btc):
	price = bf['sell']
	total = price * btc
	strP = "We are going to sell %f BTC for %f in BF, total is %f" % (btc, price, total)
	print strP
	writefile(strP)

	payload = {}
	payload['symbol'] = 'btcusd'
	payload['amount'] = str(btc)
	payload['price'] = str(price)
	payload['exchange'] = 'all'
	payload['side'] = 'sell'
	payload['type'] = 'exchange limit'
	border = bfx.order_new(payload)
	print border	

def writefile(str):
	str = datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + str
   	file_object = open('theLog1.txt', 'a')
	file_object.write(str)
	file_object.write('\n')
	file_object.close( )	
