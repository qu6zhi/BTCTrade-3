#-----------------------------
# Only support OKcoin and BitF
#-----------------------------

import okcoin
from bitf import *
import json
from  datetime  import  *
import time
from huobi import *
from btceapi import *
from btcapiall import *

_usd2cny = 6.2595
_balance = 0.008
_sell = 0.025

def compare(ok,bf):
   diff = bf['btc']*bf['price'] - bf['usd']
   if diff < -10:
      bf_status = 'cash'
   elif diff > 10:
      bf_status = 'btc'
   else:
      bf_status = 'balance'
   print "BF btc is %f,BF usd is %f,BF account status is %s, diff is %f."%(bf['btc'],bf['usd'],bf_status,diff)

   ok_price = ok['price']
   bf_price = bf['price']*_usd2cny
   dif_price = bf_price - ok_price
   rate = dif_price / ok_price
   print "OK price is %f, BF price is %f, Price different is %f, rate is %f" %(ok_price,bf_price,dif_price,rate)
  
   flag = ""
   if rate > _sell:
      if bf_status == 'cash':
	 print "Reach BF sell point, BF sold. Hold"
	 flag = "Hold"
      elif bf['sell'] > 0:
	 print "Reach BF sell point. Plan to sell"
	 return "SellBF"
      else:
	 print "Reach BF sell point. BF sell is zero"
	 return "Hold"
   elif rate < _balance and rate > (-1) * _balance:
      if bf_status == 'balance':
	 print "Reach BF Balance Point, BF is balance"
	 flag = "Hold"
      elif bf['sell'] > 0 and bf['buy'] > 0:
	 print "Reach BF balance Point. Plan to balance"
	 return "BalanceBF"
      else:
	 print "Reach BF balance point. BF sell or buy is zero"
	 return "Hold"
   elif rate < (-1) * _sell:
      if bf_status == 'btc':
	 print "Reach BF Buy Point, BF have bought"
	 flag = "Hold"
      elif bf['buy'] > 0:
	 print "Reach BF Buy Point, Plan to buy"
	 return "BuyBF"
      else:
	 print "Reach BF Buy point. BF buy is zero"
	 return "Hold"
   else:
      flag = "Hold with normal price"

   return flag

def bf_buy_ok(bfx,info_bf,auth_ok,info_ok,buy_btc):
   if info_ok['sell'] == 0:
      print "Warning! Not enough depth btc to sell btc %f, ok sell price is %f"%(sell_btc,info_ok['sell'])
      return "Fail"

   if info_ok['btc'] < buy_btc:
      print "Warning! Not enough btc %f to sell, ok btc is %f"%(buy_btc,info_ok['btc'])
      return "Fail"

   dep_btc = info_ok['sellnum'] /3
   if dep_btc < buy_btc:
      print "Warning! Not enough depth btc %f to sell, ok depth btc is %f"%(buy_btc,info_ok['sellnum'])
      return "Fail"
   
   if info_bf['buy'] == 0:
      print "Warning! Not enough depth btc to buy btc %f, BF buy is %f"%(sell_btc,info_bf['buy'])
      return "Fail"

   if info_bf['usd'] < buy_btc*info_bf['buy']:
      print "Warning! Not enough cash to buy btc %f , BF usd is %f, and BF buy price is %f"%(buy_btc,info_bf['usd'],info_bf['buy'])
      return "Fail"

   dep_btc = info_bf['buynum'] /3
   if dep_btc < buy_btc:
      print "Warning! Not enough depth btc %f to buy, BF depth btc is %f"%(buy_btc,info_bf['buynum'])
      return "Fail"

   result = ok_sell(auth_ok,info_ok,buy_btc)
   print result
   
# BF buy
   result = bf_buy(bfx,info_bf,buy_btc)
   print result
   return "OK"

def bf_sell_ok(bfx,info_bf,auth_ok,info_ok,sell_btc):
   if info_ok['buy'] == 0:
      print "Warning! Not enough depth btc to buy btc %f, ok buy is %f"%(sell_btc,info_ok['buy'])
      return "Fail"

   if info_ok['cny'] / info_ok['buy'] < sell_btc:
      print "Warning! Not enough cash to buy btc %f,OK cny is %f, OK buy price is %f"%(sell_btc,info_ok['cny'],info_ok['buy'])
      return "Fail"

   dep_btc = info_ok['buynum'] /3
   if dep_btc < sell_btc:
      print "Warning! Not enough depth btc %f to buy, ok depth btc is %f"%(sell_btc,info_ok['buynum'])
      return "Fail"
   
   if info_bf['sell'] == 0:
      print "Warning! Not enough depth btc to sell btc %f, BF sell price is %f"%(sell_btc,info_bf['sell'])
      return "Fail"

   if info_bf['btc']  < sell_btc:
      print "Warning! Not enough btc to sell btc %f,BF btc is %f"%(sell_btc,info_bf['btc'])
      return "Fail"

   dep_btc = info_bf['sellnum'] /3
   if dep_btc < sell_btc :
      print "Warning! Not enough depth btc %f to buy, OK depth btc is %f"%(sell_btc,info_ok['buynum'])
      return "Fail"

   result = ok_buy(auth_ok,info_ok,sell_btc)
   print result
# BF buy
   result = bf_sell(bfx,info_bf,sell_btc)
   print result
   return "OK"

if __name__ == "__main__":
   auth_ok = okcoin.TradeAPI('','')
   bfx = Bitfinex()
   bfx.secret = ''
   bfx.key = ''

   sleep_time = 30
   error = 0
   trade_num = 0
   while 1:
      print   'time:' , datetime.now(), 'Trade num:', trade_num

      try:
	 print "start to get info"
	 info_ok = get_info_ok(auth_ok)
	 print "got OK info!"
	 info_bf = get_info_bf(bfx)
	 print "got BF info!"
      except Exception,e:
         print str(e)
	 error = 1
      
      if error == 1:
	 error = 0
         print "Error reset"
	 time.sleep(sleep_time)
	 continue
      
      res = compare(info_ok,info_bf)
      print res
      trade = ""
      if res == "BuyBF":
	 buy_btc = info_bf['usd']/info_bf['buy'] - 0.0003
	 trade = bf_buy_ok(bfx,info_bf,auth_ok,info_ok,buy_btc)
	 print trade
      elif res == "SellBF":
	 sell_btc = info_bf['btc']
	 trade = bf_sell_ok(bfx,info_bf,auth_ok,info_ok,sell_btc)
	 print trade
      elif res == "BalanceBF":
	 diff_usd = info_bf['btc'] * info_bf['sell'] - info_bf['usd']
	 if diff_usd > 20:
	    sell_btc = diff_usd / 2 / info_bf['sell']
	    trade = bf_sell_ok(bfx,info_bf,auth_ok,info_ok,sell_btc)
	    print trade
	 elif diff_usd < -20:
	    buy_btc = (-1) * diff_usd / 2 / info_bf['buy']
	    trade = bf_buy_ok(bfx,info_bf,auth_ok,info_ok,buy_btc)
	    print trade

      if trade == "OK":
	 trade_num += 1

      time.sleep(sleep_time)

