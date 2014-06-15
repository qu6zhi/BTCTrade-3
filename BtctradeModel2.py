#---------------------------------
# sell and buy all btc in BF
# 2014.5.29 Rcihard 
# 2014.6.15 Add mode 1- BF sell  2 - Balance 3- OK sell
#--------------------------------

import okcoin
from bitf import *
import json
from  datetime  import  *
import time
from huobi import *
from btceapi import *
from btcapiall import *

_usd2cny = 6.2199
_mode = 3
_balance1 = 0.002
_bf_sell = 0.028
_balance2 = 0.003
_ok_sell = 0.020
_balance3 = 0.001
_high_diff= 0.0
_low_diff= 2.0

def compare(ok,bf):
   global _usd2cny,_mode,_high_diff,_low_diff
   
   diff = ok['btc']*ok['price'] - ok['cny']
   if diff < -200:
      ok_status = 'cash'
   elif diff > 200:
      ok_status = 'btc'
   else:
      ok_status = 'balance'
   print "$OK btc is %f,OK cny is %f,OK account status is %s, diff is %f."%(ok['btc'],ok['cny'],ok_status,diff)

   diff = bf['btc']*bf['price'] - bf['usd']
   if diff < -80:
      bf_status = 'cash'
   elif diff > 80:
      bf_status = 'btc'
   else:
      bf_status = 'balance'
   print "$BF btc is %f,BF usd is %f,BF account status is %s, diff is %f."%(bf['btc'],bf['usd'],bf_status,diff)

   ok_price = ok['price']
   bf_price = bf['price']*_usd2cny
   dif_price = bf_price - ok_price 
   rate = dif_price / ok_price
   if rate < _low_diff:
      _low_diff = rate
   if rate > _high_diff:
      _high_diff = rate
   
   print "OK price is %f, BF price is %f, Price different is %f, rate is %f, high rate is %f, low rate is %f " %(ok_price,bf_price,dif_price,rate,_high_diff,_low_diff)
   if _mode == 1:  
      flag = compare_mode1(rate,ok,bf,bf_status,ok_status)
   if _mode == 2:  
      flag = compare_mode2(rate,ok,bf,bf_status,ok_status)
   if _mode == 3:  
      flag = compare_mode3(rate,ok,bf,bf_status,ok_status)

   return flag

def compare_mode1(rate,ok,bf,bf_status,ok_status):
   global _bf_sell,_balance1 
   flag = ""
   if rate > _bf_sell:
      if bf_status == 'cash':
	 print "Reach BF sell point, BF sold. Hold"
	 flag = "Hold"
      elif bf['sell'] > 0:
	 print "Reach BF sell point. Plan to sell"
	 flag = "SellBF"
      else:
	 print "Reach BF sell point. BF sell is zero"
	 flag = "Hold"
   elif rate < _balance1: 
      if bf_status == 'btc':
	 print "Reach BF Buy Point, BF have bought"
	 flag = "Hold"
      elif bf['buy'] > 0:
	 print "Reach BF Buy Point, Plan to buy"
	 flag = "BuyBF"
      else:
	 print "Reach BF Buy point. BF buy is zero"
	 flag = "Hold"
   else:
      flag = "Hold with normal price"

   return flag

def compare_mode2(rate,ok,bf,bf_ststus,ok_ststus):
   global _bf_sell,_ok_sell,_balance2 
   flag = ""
   if rate > _bf_sell:
      if bf_status == 'cash':
	 print "Reach BF sell point, BF sold. Hold"
	 flag = "Hold"
      elif bf['sell'] > 0:
	 print "Reach BF sell point. Plan to sell"
	 flag = "SellBF"
      else:
	 print "Reach BF sell point. BF sell is zero"
	 flag = "Hold"
   elif abs(rate) < _balance1: 
      if bf_status == 'balance':
	 print "Reach BF balance point, BF have been balance"
	 flag = "Hold"
      elif bf['buy'] > 0:
	 print "Reach BF balance Point, Plan to balance"
	 flag = "Balance"
      else:
	 print "Reach BF Buy point. BF buy is zero"
	 flag = "Hold"
   elif rate < _ok_sell* (-1):
      if ok_status == 'cash':
	 print "Reach OK sell point, OK sold. Hold"
	 flag = "Hold"
      elif bf['buy'] > 0:
	 print "Reach OK sell point. Plan to sell"
	 flag = "BuyBF"
      else:
	 print "Reach OK sell point. BF buy is zero"
	 flag = "Hold"
   else:
      flag = "Hold with normal price"

   return flag

def compare_mode3(rate,ok,bf,bf_status,ok_status):
   global _ok_sell,_balance3 
   flag = ""
   if rate < _ok_sell*(-1):
      if ok_status == 'cash':
	 print "Reach OK sell point, OK sold. Hold"
	 flag = "Hold"
      elif bf['buy'] > 0 and ok['sell'] > 0:
	 print "Reach OK sell point. Plan to sell"
	 flag = "BuyBF"
      else:
	 print "Reach OK sell point. BF buy is zero or OK sell is zero"
	 flag = "Hold"
   elif rate > _balance3*(-1): 
      if ok_status == 'btc':
	 print "Reach OK Buy Point, OK have bought"
	 flag = "Hold"
      elif bf['sell'] > 0 and ok['buy']> 0:
	 print "Reach OK Buy Point, Plan to buy"
	 flag = "SellBF"
      else:
	 print "Reach OK Buy point. BF sell is zero or OK buy is zero"
	 flag = "Hold"
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
   return "Done"

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
   return "Done"

if __name__ == "__main__":
   auth_ok = okcoin.TradeAPI('','')
   bfx = Bitfinex()
   bfx.secret = ''
   bfx.key = ''

   sleep_time = 50
   error = 0
   trade_num = 0
   while 1:
      print   'time:' , datetime.now(), 'Trade num:', trade_num

      try:
	 #print "start to get info"
	 info_ok = get_info_ok(auth_ok)
	 print "got OK info, OK sell num is %f, buy num is %f "%(info_ok['sellnum'],info_ok['buynum'])
	 info_bf = get_info_bf(bfx)
	 print "got BF info, BF sell num is %f, buy num is %f "%(info_bf['sellnum'],info_bf['buynum'])

	 #info_hb = get_info_hb(hbx)
	 #print "got HB info!"
         #info_be = get_info_be(bex)
	 #print "got BE info!"
      except requests.exceptions.ConnectionError as e:
         print str(e)
	 error = 1
#      except socket.error as e:
#	 print "-------socket error"
#	 error = 1
      
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
      elif res == "Balance":
	 diff_usd = info_bf['btc'] * info_bf['sell'] - info_bf['usd']
	 if diff_usd > 50:
	    sell_btc = diff_usd / 2 / info_bf['sell']
	    trade = bf_sell_ok(bfx,info_bf,auth_ok,info_ok,sell_btc)
	    print trade
	 elif diff_usd < -50:
	    buy_btc = (-1) * diff_usd / 2 / info_bf['buy']
	    trade = bf_buy_ok(bfx,info_bf,auth_ok,info_ok,buy_btc)
	    print trade

      if trade == "OK":
	 trade_num += 1

      time.sleep(sleep_time)

