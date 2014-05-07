import okcoin
from bitf import *
import json
from  datetime  import  *
import time

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
	for i in range(59,1,-1):
		ask_amt = float(deph_ok.asks[i][0])
		if ask_amt <= up_amt:
			info_ok['buy'] = ask_amt 
        		info_ok['buynum'] += float(deph_ok.asks[i][1])
		else:
			break
 
        info_ok['sell'] = 0
	info_ok['sellnum'] = 0
	for i in range(0,59):
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
	print "We are going to sell %f BTC for %f in OK" % (btc, price)
	strP =  "We are going to sell %f BTC for %f in OK" % (btc, price)
	writefile(strP)

	result = auth.trade('btc_cny','sell',price,btc)
	print result
	
def ok_buy(auth,ok,btc):
	price = ok['buy']
	print "We are going to buy %f BTC for %f in OK" % (btc, price)
	strP =  "We are going to buy %f BTC for %f in OK" % (btc, price)
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

	up_amt = info_bf['price'] * 1.003
	down_amt = info_bf['price'] * 0.997
        
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

def trade_balance(bfx,info_bf,auth_ok,info_ok):
	diff_bf = info_bf['btc']*info_bf['price'] - info_bf['usd']
	if diff_bf > 10:
		sell_btc = info_bf['btc'] / 2
		result = bf_sell(bfx,info_bf,sell_btc)
		print result
	elif diff_bf < -10:
		buy_btc = info_bf['usd']/info_bf['buy']/2
		result = bf_buy(bfx,info_bf,buy_btc)
		print result

	diff_ok = info_ok['btc']*info_ok['price'] - info_ok['cny']
	if diff_ok > 20:
		sell_btc = info_ok['btc'] / 2
		result = ok_sell(auth_ok,info_ok,sell_btc)
		print result
	elif diff_ok < -20:
		buy_btc = info_ok['cny']/info_ok['buy']/2
		result = ok_buy(auth_ok,info_ok,buy_btc)
		print result

def compare(ok,bf):
	usd2cny = 6.2595
	
	diff = ok['btc']*ok['price'] - ok['cny']
	if diff < -100:
		ok_status = 'cash'
	elif diff > 100:
		ok_status = 'btc'
	else:
		ok_status = 'balance'
	print "OK btc is %f,OK cny is %f,OK account status is %s, diff is %f."%(ok['btc'],ok['cny'],ok_status,diff)

	diff = bf['btc']*bf['price'] - bf['usd']
	if diff < -10:
		bf_status = 'cash'
	elif diff > 10:
		bf_status = 'btc'
	else:
		bf_status = 'balance'
	print "BF btc is %f,BF usd is %f,BF account status is %s, diff is %f."%(bf['btc'],bf['usd'],bf_status,diff)

	ok_price = ok['price']
	bf_price = bf['price']*usd2cny
	dif_price = bf_price - ok_price
	rate = dif_price / ok_price
	print "OK price is %f, BF price is %f" %(ok_price,bf_price)
	print "Price different is %f, rate is %f" %(dif_price,rate)
	
	if ok['f_cny'] <> 0 or ok['f_btc'] <> 0:
		print "OK have pending order"
		return "hold"
	elif bf['f_usd'] <> 0 or bf['f_btc'] <> 0:
		print "BF have pending order"
		return "hold"
	elif rate > 0.016:
		if bf_status == 'cash':
			print "bf selled"
			return "hold"

		bf_sell = bf['sell'] * usd2cny
		diff = bf_sell - ok['buy']
		wrate = diff / ok['buy']
		print "bf sell is %f, ok buy is %f, diff is %f, rate is %f."%(bf_sell,ok['buy'],diff,wrate)
		if wrate > 0.011:
			brate = bf['sellnum']/bf['btc']
			print "(BF)bf plan to sell btc  %f, bf sell btc deph is %f, rate is %f."%(bf['btc'],bf['sellnum'],brate) 
			
			obtc = ok['cny']/ok['buy']
			orate = ok['buynum']/obtc
			print "(BF)ok plan to buy btc is %f, ok buy btc deph is %f, rate is %f." %(obtc,ok['buynum'],orate)
 
			if brate >= 3 and orate >= 3:
				return "bf_sell"
			else:
				return "hold"

	elif rate < 0.0015 and rate > -0.0015:
		if bf_status == 'balance':
			print "bf is balance"
			return "hold"

		if ok_status == 'cash':
			obtc = ok['cny']/2/ok['buy']
			orate = ok['buynum']/obtc
			print "(BL)ok plan to buy btc is %f, ok buy btc deph is %f, rate is %f." %(obtc,ok['buynum'],orate)

			bbtc = bf['btc']/2 
			brate = bf['sellnum']/bbtc
			print "(BL)bf plan to sell btc is %f, bf sell btc deph is %f, rate is %f."%(bbt,bf['sellnum'],brate)

			if orate >=3 and brate >=3:
				return 'balance'
			else:
				return 'hold'

		if bf_status == 'cash':
			bbtc = bf['usd']/2/bf['buy']
			brate = bf['buynum']/bbtc
			print "(BL)BF plan to buy btc is %f, bf buy btc deph is %f, rate is %f." %(bbtc,bf['buynum'],brate)

			obtc = ok['btc']/2 
			orate = ok['sellnum']/obtc
			print "(BL)OK plan to sell btc is %f, OK sell btc deph is %f, rate is %f."%(obtc,ok['sellnum'],orate)

			if orate >=3 and brate >=3:
				return 'balance'
			else:
				return 'hold'

	elif rate < -0.016:
		if ok_status == 'cash':
			print "ok selled"
			return "hold"

		bf_buy = bf['usd'] * usd2cny
		diff = ok['sell'] - bf_buy
		wrate = diff / ok['buy']
		print "OK sell is %f, BF buy is %f, diff is %f, rate is %f."%(ok['sell'],bf_buy,diff,wrate)
		if wrate > 0.011:
			orate = ok['sellnum']/ok['btc']
			print "(OK)OK plan to sell btc %f, OK sell btc deph is %f, rate is %f."%(ok['btc'],ok['sellnum'],orate) 
			
			bbtc = bf['usd']/bf['buy']
			brate = bf['buynum']/obtc
			print "(OK)BF plan to buy btc is %f, BF buy btc deph is %f, rate is %f." %(bbtc,bf['buynum'],brate)
 
			if brate >= 3 and orate >= 3:
				return "ok_sell"
			else:
				return "hold"
	
	return "Hold with normal price"

def bf_buy(bfx,bf,btc):
	amt = bf['buy']
	print "We are going to buy %f BTC for %f in BF" % (btc, amt)
	strP =  "We are going to buy %f BTC for %f in BF" % (btc, amt)
	writefile(strP)

	payload = {}
	payload['symbol'] = 'btcusd'
	payload['amount'] = str(btc)
	payload['price'] = str(amt)
	payload['exchange'] = 'all'
	payload['side'] = 'buy'
	payload['type'] = 'exchange limit'
	border = bfx.order_new(payload)
	print border	

def bf_sell(bfx,bf,btc):
	amt = bf['sell']
	print "We are going to sell %f BTC for %f in BF" % (btc, amt)
	strP = "We are going to sell %f BTC for %f in BF" % (btc, amt)
	writefile(strP)

	payload = {}
	payload['symbol'] = 'btcusd'
	payload['amount'] = str(btc)
	payload['price'] = str(amt)
	payload['exchange'] = 'all'
	payload['side'] = 'sell'
	payload['type'] = 'exchange limit'
	border = bfx.order_new(payload)
	print border	

def writefile(str):
	file_object = open('theLog1.txt', 'a')
	file_object.write(str)
	file_object.write('\n')
	file_object.close( )	

if __name__ == "__main__":
# get OKcoin info
 	auth_ok = okcoin.TradeAPI('','')

	bfx = Bitfinex()
	bfx.secret = ''
	bfx.key = ''

	sleep_time = 100
	error = 0
	trade_num = 0
	while 1:
		print   'time:' , datetime.now()
 		print   'Trade num:',trade_num
		info_ok = get_info_ok(auth_ok)
#		print info_ok
		info_bf = get_info_bf(bfx)
#		print info_bf

		result = compare(info_ok,info_bf)
		print result
	
		if result == 'balance':
		 	timestr =   'time:%s' %( datetime.now())
			writefile(timestr)

			result = trade_balance(bfx,info_bf,auth_ok,info_ok)
			print result
			trade_num +=1
		elif result == 'ok_sell':
		 	timestr =   'time:%s' %( datetime.now())
			writefile(timestr)

			btc = info_ok['btc']
			result = ok_sell(auth_ok,info_ok,btc)
			print result
			
			btc = info_bf['usd']/info_bf['buy'] - 0.0005
			result = bf_buy(bfx,info_bf,btc)
			print result
			trade_num +=1
		elif result == 'bf_sell':
		 	timestr =   'time:%s' %( datetime.now())
			writefile(timestr)

			btc = info_bf['btc']
			result = bf_sell(bfx,info_bf,btc)
			print result

			btc = info_ok['cny']/info_ok['buy'] - 0.0005
			result = ok_buy(auth_ok,info_ok,btc)
			print result
			trade_num +=1
		
		time.sleep(sleep_time)
