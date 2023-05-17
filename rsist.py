import ccxt
import pandas as pd
import time
import pprint
import requests
import numpy as np
import talib

webhook_url = 'https://discordapp.com/api/webhooks/1095655937735413772/pmE27Cok8_W-arSpcpwfhE_uOm_h5VQZG-gbv-vWnUk1cs9H6x3TBPpWPo49KWaqTRo_'


exc = {'content': '오류발생'}
inlong={'content':'long진입'}
outlong={'content':'long close'}
inshort={'content':'short in'}
outshort={'content':'short close'}


# def heiken_ashi(df):
#     # 하이킨 아시 캔들 차트를 계산하는 함수

#     ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
#     ha_open = (df['open'].shift(1) + df['close'].shift(1)) / 2
#     ha_high = df[['high', 'close']].max(axis=1)
#     ha_low = df[['low', 'close']].min(axis=1)

#     df['ha_close'] = ha_close
#     df['ha_open'] = ha_open
#     df['ha_high'] = ha_high
#     df['ha_low'] = ha_low

#     return df
# def setema(ohlcvs,ema_period):
#     prices = np.zeros(len(ohlcvs))
#     ema_values = np.zeros(len(ohlcvs))
#     # 종가만 추출하여 prices 배열에 저장
#     for i in range(len(ohlcvs)):
#         prices[i] = ohlcvs[i][4]

#     # 첫 번째 EMA 값은 SMA(단순 이동 평균)으로 계산
#     sma = np.sum(prices[:ema_period]) / ema_period
#     ema_values[ema_period - 1] = sma

#     # EMA 계산
#     multiplier = 2 / (ema_period + 1)
#     for i in range(ema_period, len(prices)):
#         ema = (prices[i] - ema_values[i - 1]) * multiplier + ema_values[i - 1]
#         ema_values[i] = ema
#     return ema_values[-1]

api_key = ""
secret  = ""

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})





#*************************설정***************************************************************************
# 시장(symbol) 설정 (예: BTC/USDT)
symbol = 'BTC/USDT'#<<<<<<<<<<<<<<<<<<<<<코인 설정
inputper=33  #<<<<<<<<<<<<<진입량per
lev=33 #<<<<<<<<<<<<<<<<레버리지
timeframe = '15m'# 타임프레임(timeframe) 설정 (예: 15분)
#슈퍼트렌드 설정
# period = 10     
# multiplier = 3



#editsym=symbol.replace("/","")
markets = binance.load_markets()
market = binance.market(symbol)
editsym=market['id']


#슈퍼트렌드 기모띠 Long==true
# def Supertrend(df, atr_period, multiplier):
    
#     high = df['high']
#     low = df['low']
#     close = df['close']
    
#     # calculate ATR
#     price_diffs = [high - low, 
#                    high - close.shift(), 
#                    close.shift() - low]
#     true_range = pd.concat(price_diffs, axis=1)
#     true_range = true_range.abs().max(axis=1)
#     # default ATR calculation in supertrend indicator
#     atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
#     # df['atr'] = df['tr'].rolling(atr_period).mean()
    
#     # HL2 is simply the average of high and low prices
#     hl2 = (high + low) / 2
#     # upperband and lowerband calculation
#     # notice that final bands are set to be equal to the respective bands
#     final_upperband = upperband = hl2 + (multiplier * atr)
#     final_lowerband = lowerband = hl2 - (multiplier * atr)
    
    # initialize Supertrend column to True
    # supertrend = [True] * len(df)
    
    # for i in range(1, len(df.index)):
    #     curr, prev = i, i-1
        
    #     # if current close price crosses above upperband
    #     if close[curr] > final_upperband[prev]:
    #         supertrend[curr] = True
    #     # if current close price crosses below lowerband
    #     elif close[curr] < final_lowerband[prev]:
    #         supertrend[curr] = False
    #     # else, the trend continues
    #     else:
    #         supertrend[curr] = supertrend[prev]
            
    #         # adjustment to the final bands
    #         if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
    #             final_lowerband[curr] = final_lowerband[prev]
    #         if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
    #             final_upperband[curr] = final_upperband[prev]

    #     # to remove bands according to the trend direction
    #     if supertrend[curr] == True:
    #         final_upperband[curr] = np.nan
    #     else:
    #         final_lowerband[curr] = np.nan
    
    # return pd.DataFrame({
    #     'Supertrend': supertrend,
    #     'Lowerband': final_lowerband,
    #     'Upperband': final_upperband
    # }, index=df.index)






#레버리지 설정 코드
resp = binance.fapiPrivate_post_leverage({
    'symbol': editsym,
    'leverage': lev
})




# 데이터 개수 설정 (예: 최근 100개)
limit = 50
#자산 진입량 변환 함수
def amtper(a,c=1):#a==진입 퍼센트 c==leverage 현재사용가능한 자산에 a퍼센트만큼 c레버리지 양만큼 구매
    balance = binance.fetch_balance()
    b=(balance['USDT']['free'])
    totalinput=b*a*c/100
    ticker = binance.fetch_ticker(symbol)
    cur_price=ticker['close']
    amt=totalinput/cur_price
    return round(amt,4)
    
isrsi=0
isstost=0
try:
    while True:
        print("루프시작")
        # 바이낸스 API로 OHLCV 데이터 가져오기
        ohlcvs = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcvs, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # 타임스탬프를 날짜/시간 형식으로 변환
        df.set_index('timestamp', inplace=True)  # 인덱스를 날짜/시간으로 설정
       
        # # MACD
        # macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        # df['macd'] = macd
        # df['macdsignal'] = macdsignal

        # RSI
        rsi = talib.RSI(df['close'], timeperiod=14)
        df['rsi'] = rsi

        def stoch_rsi(close, rsi_length=14, stoch_length=14, smooth_k=3, smooth_d=3):
            rsi = talib.RSI(close, timeperiod=rsi_length)
            stoch_rsi_min = np.array(
                [np.nan if np.isnan(x) else np.min(rsi[max(int(idx - stoch_length + 1), 0):int(idx + 1)]) for idx, x in enumerate(rsi)]
            )
            stoch_rsi_max = np.array(
                [np.nan if np.isnan(x) else np.max(rsi[max(int(idx - stoch_length + 1), 0):int(idx + 1)]) for idx, x in enumerate(rsi)]
            )
            stoch_rsi = (rsi - stoch_rsi_min) / (stoch_rsi_max - stoch_rsi_min)

            k = talib.SMA(stoch_rsi, timeperiod=smooth_k)
            d = talib.SMA(k, timeperiod=smooth_d)

            return round(k,5)*100 ,round(d,5)*100

        df['k'], df['d'] = stoch_rsi(df['close'])


        # #볼륨오실레이터
        # # 거래량 데이터의 총합 구하기
        # cum_volume = sum(df['volume'])
        # if cum_volume == 0:
        #     raise ValueError("No volume is provided by the data vendor.")

        # # stoch %K, %D 값 구하기
        # short = talib.EMA(df['volume'].to_numpy(), timeperiod=5)
        # long = talib.EMA(df['volume'].to_numpy(), timeperiod=10)
        # osc = 100 * (short - long) / long

        # # 결과값 소수점 세 번째 자리에서 반올림(round)하여 출력
        # df['osc'] = np.append(np.zeros(len(df)-len(osc)), osc)
        
        

        

        # 하이킨 아시 캔들 차트로 변환
        # heidf = heiken_ashi(df)

        #포지션 존재하는지 검증 코드
        balance = binance.fetch_balance()
        positions = balance['info']['positions']
        posiamt=0
        for position in positions:
            if position["symbol"] == editsym:
                # pprint.pprint(position)
                posiamt=position['positionAmt']
                unprofit=position['unrealizedProfit']
                entryprice=position['entryPrice']
        posiamt=float(posiamt)
        unprofit=float(unprofit)
        entryprice=float(entryprice)
        absposi=abs(posiamt)
        
        #현재 가격
        currentprice=df.iloc[-1]['close']
        cur_rsi=df.iloc[-1]['rsi']
        #cur_mac=df.iloc[-1]['macd']
        #cur_macsig=df.iloc[-1]['macdsignal']
        cur_d= df.iloc[-1]['d']
        cur_k= df.iloc[-1]['k']
        #cur_osc=df.iloc[-1]['osc']
    

        


        
        

        # 현재 진행 중인 봉의 이전 봉
        # current_candle = heidf.iloc[-1]
        # previous_candle = heidf.iloc[-2]
        
        #진입코드 설정
        
        #횡보장 스토 전략
        # while posiamt==0 and cur_rsi<=69 and cur_rsi>=31 and isstost==0:
        #     print("횡보장 sto 전략확인")
        #     if cur_d<=4:
        #         order = binance.create_market_buy_order(
        #         symbol=symbol,
        #         amount=amtper(inputper,lev))
        #         response = requests.post(webhook_url, json=inlong)
        #         isstost=1
        #         time.sleep(10)
        #         break
        #     if cur_d>=96:
        #         order = binance.create_market_sell_order(
        #         symbol=symbol,
        #         amount=amtper(inputper,lev))
        #         response = requests.post(webhook_url, json=inshort)
        #         isstost=1
        #         time.sleep(10)
        #         break
        #     else:
        #         time.sleep(10)
        #         break
        # #sto 정리
        # while isstost==1 and posiamt!=0 :
        #     print("sto 정리")
        #     if cur_k>=96 and posiamt>0:
        #         order = binance.create_market_sell_order(
        #         symbol=symbol,
        #         amount=absposi)
        #         response = requests.post(webhook_url, json=outlong)
        #         isstost=0
        #         time.sleep(10)
        #         break
        #     if cur_k<=4 and posiamt<0:
        #         order = binance.create_market_buy_order(
        #         symbol=symbol,
        #         amount=absposi)
        #         response = requests.post(webhook_url, json=outshort)
        #         isstost=0
        #         time.sleep(10)
        #         break
        #     else:
        #         time.sleep(5)
        #         break
        #손절및 익절코드
        while posiamt!=0 :
            print("손익절 루프")
            # #sto손절
            # if posiamt>0 and cur_rsi<=27 and isstost==1:
            #     order = binance.create_market_sell_order(
            #     symbol=symbol,
            #     amount=absposi)
            #     response = requests.post(webhook_url, json=outlong)
            #     isstost=0
            #     time.sleep(10)
            #     break
            # if posiamt<0 and cur_rsi>=73 and isstost==1:
            #     order = binance.create_market_buy_order(
            #     symbol=symbol,
            #     amount=absposi)
            #     response = requests.post(webhook_url, json=outshort)
            #     isstost=0
            #     time.sleep(10)
            #     break
            #rsi 정리
            if posiamt<0 and cur_rsi<=67 and isrsi==1:
                order = binance.create_market_buy_order(
                symbol=symbol,
                amount=absposi)
                response = requests.post(webhook_url, json=outshort)
                isrsi=0
                time.sleep(10)
                break
            if posiamt>0 and cur_rsi>=33 and isrsi==1:
                order = binance.create_market_sell_order(
                symbol=symbol,
                amount=absposi)
                response = requests.post(webhook_url, json=outlong)
                isrsi=0
                time.sleep(10)
                break
            

            #rsi 분할매수 매도
            if posiamt<0 and cur_rsi<=73 and isrsi==2:
                order = binance.create_market_buy_order(
                symbol=symbol,
                amount=round((absposi/2),1))
                response = requests.post(webhook_url, json=outshort)
                isrsi=1
                time.sleep(10)
                break
            if posiamt>0 and cur_rsi>=27 and isrsi==2:
                order = binance.create_market_sell_order(
                symbol=symbol,
                amount=round((absposi/2),1))
                response = requests.post(webhook_url, json=outlong)
                isrsi=1
                time.sleep(10)
                break
            else:
                time.sleep(5)
                break
            

        #rsi 전략
        while (cur_rsi>=70 or cur_rsi<=30) and posiamt==0 and isrsi==0:
            print("rsi루프")
            if cur_rsi>=79:
                order = binance.create_market_sell_order(
                symbol=symbol,
                amount=amtper(inputper,lev))
                response = requests.post(webhook_url, json=inshort)
                isrsi=1
                time.sleep(10)
                break
            if cur_rsi<=21:
                order = binance.create_market_buy_order(
                symbol=symbol,
                amount=amtper(inputper,lev))
                response = requests.post(webhook_url, json=inlong)
                isrsi=1
                time.sleep(10)
                break
            else:
                time.sleep(10)
                break
            #rsi 분할 매수
        while isrsi==1 and (cur_rsi>=77 or cur_rsi<=23):
            if cur_rsi>=84:
                order = binance.create_market_sell_order(
                symbol=symbol,
                amount=amtper(inputper,lev))
                response = requests.post(webhook_url, json=inshort)
                isrsi=2
                time.sleep(10)
                break
            if cur_rsi<=16:
                order = binance.create_market_buy_order(
                symbol=symbol,
                amount=amtper(inputper,lev))
                response = requests.post(webhook_url, json=inlong)
                isrsi=2
                time.sleep(10)
                break
            else:
                time.sleep(10)
                break


        time.sleep(10)
                






except Exception as ex:
    print(ex)
    response = requests.post(webhook_url, json=exc)

            
            




























   

    
