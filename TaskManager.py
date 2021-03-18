from binance.enums import ORDER_TYPE_MARKET,KLINE_INTERVAL_1MINUTE,SIDE_BUY,SIDE_SELL,TIME_IN_FORCE_GTC


def order(client,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        
        #order = client.create_test_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        orderJson = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(orderJson)
        
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def getBalance(client, symbol):
    response= client.get_asset_balance(asset=symbol)
    balance= 0
    if response != None and 'free' in response:
        balance= float(response['free'])
        
    print('Current Balance for %s:\t%s'%(symbol, balance))
    return balance
    

def isInOrder(client, symbol, TRADE_QUANTITY):
    balance= getBalance(client,symbol)
    if balance > TRADE_QUANTITY:
        return True
    return False

def orderMargin(client,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        orderJson = client.create_margin_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_MARKET,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=quantity)
        print(orderJson)
        
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True
    