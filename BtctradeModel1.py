import okcoin
from bitf import *
import json
from  datetime  import  *
import time
from huobi import *
from btceapi import *
from btcapiall import *

_usd2cny = 6.2595

def compare(ok,bf,be):
   diff = bf['btc']*bf['price'] - bf['usd']
   if diff < -20:
      bf_status = 'cash'
   elif diff > 20:
      bf_status = 'btc'
   else:
      bf_status = 'balance'
      print "BF btc is %f,BF usd is %f,BF account status is %s, diff is %f."%(bf['btc'],bf['usd'],bf_status,diff)

   diff = be['btc']*be['price'] - be['usd']
   if diff < -20:
      be_status = 'cash'
   elif diff > 20:
      be_status = 'btc'
   else:
      be_status = 'balance'

   ok_price = ok['price']
   bf_price = bf['price']*_usd2cny
   dif_price = bf_price - ok_price
   rate = dif_price / ok_price
   print "OK price is %f, BF price is %f, Price different is %f, rate is %f" %(ok_price,bf_price,dif_price,rate)
  
   flag = ""
   if rate > 0.016:
      if bf_status == 'cash':
	 print "Reach BF sell point, BF sold. Hold"
	 flag = "Hold"
      else:
	 print "Reach BF sell point. Plan to sell"
	 return "SellBF"
   elif rate < 0.0015 and rate > -0.0015:
      if bf_status == 'balance':
	 print "Reach BF Balance Point, BF is balance"
	 flag = "Hold"
      else:
	 print "Reach BF balance Point. Plan to balance"
	 return "BalanceBF"
   elif rate < -0.016:
      if bf_status == 'btc':
	 print "Reach BF Buy Point, BF have bought"
	 flag = "Hold"
      else:
	 print "Reach BF Buy Point, Plan to buy"
	 return "BuyBF"
   else:
      flag = "Hold"

# compare BE and OK
   if flag == "Hold":
      ok_price = ok['price']
      be_price = be['price']*_usd2cny
      dif_price = be_price - ok_price
      rate = dif_price / ok_price
      print "OK price is %f, BE price is %f, Price different is %f, rate is %f" %(ok_price,be_price,dif_price,rate)
      if rate > 0.016:
	 if be_status == 'cash':
	    print "Reach BE sell point, BE sold. Hold"
	    return "Hold"
	 else:
	    print "Reach BE sell point. Plan to sell"
	    return "SellBE"
      elif rate < 0.0015 and rate > -0.0015:
	 if bf_status == 'balance':
	    print "Reach BE Balance Point, BE is balance"
	    return "Hold"
	 else:
	    print "Reach BE balance Point. Plan to balance"
	    return "BalanceBE"
      elif rate < -0.016:
	 if bf_status == 'btc':
	    print "Reach BE Buy Point, BE have bought"
	    return "Hold"
	 else:
	    print "Reach BE Buy Point, Plan to buy"
	    return "BuyBE"
      else:
	 return "Hold with normal price"

def bf_buy_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,buy_btc):

   if info_hb['btc'] + info_ok['btc'] < buy_btc:
      print "Warning! Not enough btc %f to sell,hb btc is %f, ok btc is %f"%(buy_btc,info_hb['btc'],info_ok['btc'])
      return "Fail"

   dep_btc = info_hb['sellnum'] / 3 + info_ok['sellnum'] /3
   if dep_btc < buy_btc:
      print "Warning! Not enough depth btc %f to sell, hb depth btc is %f, ok depth btc is %f"%(buy_btc,info_hb['sellnum'],info_ok['sellnum'])
      return "Fail"
   
   flag = ""
   # Case 0: sell all btc in OK
   if buy_btc > info_ok['sellnum'] / 3 and buy_btc < info_ok['btc']:
      result = ok_sell(auth_ok,info_ok,buy_btc)
      print result
      flag =  "OK"
   
   # Case 1: Sell all btc in OK and sell rest of it in HB
   diff_ok1 = buy_btc - info_ok['btc']
   trad_ok1 = info_ok['sellnum'] / 3  - info_ok['btc']
   diff_hb1 = info_hb['btc'] - diff_ok1
   trad_hb1 = info_hb['sellnum'] / 3 - diff_ok1
   if flag == "" and diff_ok1 > 0 and trad_ok1 > 0 and diff_hb1 >0 and trad_hb1 > 0:
      result = ok_sell(auth_ok,info_ok,info_ok['btc'])
      print result
      result = hb_sell(hbx,info_hb,diff_ok1)
      print result
      flag = "OK"
      
   # Case 2: Sell all btc in HB and sell rest of it in OK
   diff_hb2 = buy_btc - info_hb['btc']
   trad_hb2 = info_hb['sellnum'] / 3  - info_hb['btc']
   diff_ok2 = info_ok['btc'] - diff_hb2
   trad_ok2 = info_ok['sellnum'] / 3 - diff_hb2
   if flag == "" and diff_hb2 > 0 and trad_hb2 > 0 and diff_ok2 >0 and trad_ok2 > 0:
      result = hb_sell(hbx,info_hb,info_hb['btc'])
      print result
      result = ok_sell(auth_ok,info_ok,diff_hb2)
      print result
      flag = "OK"

   if flag == "OK":
# BF buy
      result = bf_buy(bfx,info_bf,buy_btc)
      print result
      return "OK"
   else:
      print "Can not find trade chance, OK info is"
      print info_ok
      print "HB info is"
      print info_ok
      return "Fail"

def bf_sell_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,sell_btc):
   if info_hb['buy'] == 0 or info_ok['buy'] == 0:
      print "Warning! Not enough depth btc to buy btc %f,hb buy is %f, ok buy is %f"%(sell_btc,info_hb['buy'],info_ok['buy'])
      return "Fail"

   if info_hb['cny'] / info_hb['buy']  + info_ok['cny'] / info_ok['buy'] < sell_btc:
      print "Warning! Not enough cash to buy btc %f,hb cny is %f, ok cny is %f"%(sell_btc,info_hb['cny'],info_ok['cny'])
      return "Fail"

   dep_btc = info_hb['buynum'] / 3 + info_ok['buynum'] /3
   if dep_btc < sell_btc:
      print "Warning! Not enough depth btc %f to buy, hb depth btc is %f, ok depth btc is %f"%(sell_btc,info_hb['buynum'],info_ok['buynum'])
      return "Fail"
   
   flag = ""
   # Case 0: buy all btc in OK
   if sell_btc > info_ok['buynum'] / 3 and sell_btc < info_ok['cny'] / info_ok['buy']:
      result = ok_buy(auth_ok,info_ok,sell_btc)
      print result
      flag =  "OK"
   
   # Case 1: Buy all btc in OK and buy rest of it in HB
   btc_ok1 = info_ok['cny'] / info_ok['buy'] - 0.0003
   diff_ok1 = sell_btc - btc_ok1
   trad_ok1 = info_ok['buynum'] / 3  - btc_ok1
   diff_hb1 = info_hb['cny'] / info_hb['buy'] - diff_ok1
   trad_hb1 = info_hb['buynum'] / 3 - diff_ok1
   if flag == "" and diff_ok1 > 0 and trad_ok1 > 0 and diff_hb1 >0 and trad_hb1 > 0:
      result = ok_buy(auth_ok,info_ok,btc_ok1)
      print result
      result = hb_buy(hbx,info_hb,diff_ok1)
      print result
      flag = "OK"
      
   # Case 2: Sell all btc in HB and sell rest of it in OK
   btc_hb2 = info_hb['cny'] / info_hb['buy'] - 0.0003
   diff_hb2 = sell_btc - btc_hb2
   trad_hb2 = info_hb['buynum'] / 3  - btc_hb2
   diff_ok2 = info_ok['cny'] / info_ok['buy'] - diff_hb2
   trad_ok2 = info_ok['buynum'] / 3 - diff_hb2
   if flag == "" and diff_hb2 > 0 and trad_hb2 > 0 and diff_ok2 >0 and trad_ok2 > 0:
      result = hb_buy(hbx,info_hb,btc_hb2)
      print result
      result = ok_buy(auth_ok,info_ok,diff_hb2)
      print result
      flag = "OK"

   if flag == "OK":
# BF buy
      result = bf_sell(bfx,info_bf,sell_btc)
      print result
      return "OK"
   else:
      print "Can not find trade chance, OK info is"
      print info_ok
      print "HB info is"
      print info_ok
      return "Fail"

def be_buy_okhb(bex,info_be,auth_ok,info_ok,hbx,info_hb,buy_btc):

   if info_hb['btc'] + info_ok['btc'] < buy_btc:
      print "Warning! Not enough btc %f to sell,hb btc is %f, ok btc is %f"%(buy_btc,info_hb['btc'],info_ok['btc'])
      return "Fail"

   dep_btc = info_hb['sellnum'] / 3 + info_ok['sellnum'] /3
   if dep_btc < buy_btc:
      print "Warning! Not enough depth btc %f to sell, hb depth btc is %f, ok depth btc is %f"%(buy_btc,info_hb['sellnum'],info_ok['sellnum'])
      return "Fail"
   
   flag = ""
   # Case 0: sell all btc in HB
   if buy_btc > info_hb['sellnum'] / 3 and buy_btc < info_hb['btc']:
      result = hb_sell(hbx,info_hb,buy_btc)
      print result
      flag =  "OK"
   
   # Case 1: Sell all btc in OK and sell rest of it in HB
   diff_ok1 = buy_btc - info_ok['btc']
   trad_ok1 = info_ok['sellnum'] / 3  - info_ok['btc']
   diff_hb1 = info_hb['btc'] - diff_ok1
   trad_hb1 = info_hb['sellnum'] / 3 - diff_ok1
   if flag == "" and diff_ok1 > 0 and trad_ok1 > 0 and diff_hb1 >0 and trad_hb1 > 0:
      result = ok_sell(auth_ok,info_ok,info_ok['btc'])
      print result
      result = hb_sell(hbx,info_hb,diff_ok1)
      print result
      flag = "OK"
      
   # Case 2: Sell all btc in HB and sell rest of it in OK
   diff_hb2 = buy_btc - info_hb['btc']
   trad_hb2 = info_hb['sellnum'] / 3  - info_hb['btc']
   diff_ok2 = info_ok['btc'] - diff_hb2
   trad_ok2 = info_ok['sellnum'] / 3 - diff_hb2
   if flag == "" and diff_hb2 > 0 and trad_hb2 > 0 and diff_ok2 >0 and trad_ok2 > 0:
      result = hb_sell(hbx,info_hb,info_hb['btc'])
      print result
      result = ok_sell(auth_ok,info_ok,diff_hb2)
      print result
      flag = "OK"

   if flag == "OK":
# BF buy
      result = be_buy(bex,info_bf,buy_btc)
      print result
      return "OK"
   else:
      print "Can not find trade chance, OK info is"
      print info_ok
      print "HB info is"
      print info_ok
      return "Fail"

def be_sell_okhb(bex,info_bf,auth_ok,info_ok,hbx,info_hb,sell_btc):
   if info_hb['buy'] == 0 or info_ok['buy'] == 0:
      print "Warning! Not enough depth btc to buy btc %f,hb buy is %f, ok buy is %f"%(sell_btc,info_hb['buy'],info_ok['buy'])
      return "Fail"

   if info_hb['cny'] / info_hb['buy']  + info_ok['cny'] / info_ok['buy'] < sell_btc:
      print "Warning! Not enough cash to buy btc %f,hb cny is %f, ok cny is %f"%(sell_btc,info_hb['cny'],info_ok['cny'])
      return "Fail"

   dep_btc = info_hb['buynum'] / 3 + info_ok['buynum'] /3
   if dep_btc < sell_btc:
      print "Warning! Not enough depth btc %f to buy, hb depth btc is %f, ok depth btc is %f"%(sell_btc,info_hb['buynum'],info_ok['buynum'])
      return "Fail"
   
   flag = ""
   # Case 0: buy all btc in HB
   if sell_btc > info_hb['buynum'] / 3 and sell_btc < info_hb['cny'] / info_hb['buy']:
      result = hb_buy(hbx,info_hb,sell_btc)
      print result
      flag =  "OK"
   
   # Case 1: Buy all btc in OK and buy rest of it in HB
   btc_ok1 = info_ok['cny'] / info_ok['buy'] - 0.0003
   diff_ok1 = sell_btc - btc_ok1
   trad_ok1 = info_ok['buynum'] / 3  - btc_ok1
   diff_hb1 = info_hb['cny'] / info_hb['buy'] - diff_ok1
   trad_hb1 = info_hb['buynum'] / 3 - diff_ok1
   if flag == "" and diff_ok1 > 0 and trad_ok1 > 0 and diff_hb1 >0 and trad_hb1 > 0:
      result = ok_buy(auth_ok,info_ok,btc_ok1)
      print result
      result = hb_buy(hbx,info_hb,diff_ok1)
      print result
      flag = "OK"
      
   # Case 2: Sell all btc in HB and sell rest of it in OK
   btc_hb2 = info_hb['cny'] / info_hb['buy'] - 0.0003
   diff_hb2 = sell_btc - btc_hb2
   trad_hb2 = info_hb['buynum'] / 3  - btc_hb2
   diff_ok2 = info_ok['cny'] / info_ok['buy'] - diff_hb2
   trad_ok2 = info_ok['buynum'] / 3 - diff_hb2
   if flag == "" and diff_hb2 > 0 and trad_hb2 > 0 and diff_ok2 >0 and trad_ok2 > 0:
      result = hb_buy(hbx,info_hb,btc_hb2)
      print result
      result = ok_buy(auth_ok,info_ok,diff_hb2)
      print result
      flag = "OK"

   if flag == "OK":
# BF buy
      result = be_sell(bex,info_bf,sell_btc)
      print result
      return "OK"
   else:
      print "Can not find trade chance, OK info is"
      print info_ok
      print "HB info is"
      print info_ok
      return "Fail"

if __name__ == "__main__":
   auth_ok = okcoin.TradeAPI('','')
   bfx = Bitfinex()
   bfx.secret = ''
   bfx.key = ''
   hbx = HuoBi('','')
   bex = btce('','')

   sleep_time = 30
   error = 0
   trade_num = 0
   while 1:
      print   'time:' , datetime.now(), 'Trade num:', trade_num

      try:
	 info_ok = get_info_ok(auth_ok)
	 info_bf = get_info_bf(bfx)
	 info_hb = get_info_hb(hbx)
         info_be = get_info_be(bex)
      except Exception,e:
         print str(e)
	 error = 1
      
      if error == 1:
	 error = 0
	 time.sleep(sleep_time)
	 continue
      
      res = compare(info_ok,info_bf,info_be)
      print res
      trade = ""
      if res == "BuyBF":
	 buy_btc = info_bf['usd']/info_bf['buy'] - 0.0003
	 trade = bf_buy_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,buy_btc)
	 print trade
      elif res == "SellBF":
	 sell_btc = info_bf['btc']
	 trade = bf_sell_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,sell_btc)
	 print trade
      elif res == "BalanceBF":
	 diff_usd = info_bf['btc'] * info_bf['sell'] - info_bf['usd']
	 if diff_usd > 20:
	    sell_btc = diff_usd / 2 / info_bf['sell']
	    trade = bf_sell_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,sell_btc)
	    print trade
	 elif diff_usd < -20:
	    buy_btc = (-1) * diff_usd / 2 / info_bf['buy']
	    trade = bf_buy_okhb(bfx,info_bf,auth_ok,info_ok,hbx,info_hb,buy_btc)
	    print trade
      elif res == "BuyBE":
	 buy_btc = info_be['usd']/info_be['buy'] - 0.0003
	 trade = be_buy_okhb(bex,info_be,auth_ok,info_ok,hbx,info_hb,buy_btc)
	 print trade
      elif res == "SellBE":
	 sell_btc = info_be['btc']
	 trade = be_sell_okhb(bex,info_be,auth_ok,info_ok,hbx,info_hb,sell_btc)
	 print trade
      elif res == "BalanceBF":
	 diff_usd = info_be['btc'] * info_be['sell'] - info_be['usd']
	 if diff_usd > 20:
	    sell_btc = diff_usd / 2 / info_be['sell']
	    trade = be_sell_okhb(bex,info_be,auth_ok,info_ok,hbx,info_hb,sell_btc)
	    print trade
	 elif diff_usd < -20:
	    buy_btc = (-1) * diff_usd / 2 / info_be['buy']
	    trade = be_buy_okhb(bex,info_be,auth_ok,info_ok,hbx,info_hb,buy_btc)

      if trade == "OK":
	 trade_num += 1

      time.sleep(sleep_time)


