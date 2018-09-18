import sys
import socket
import json
import time

team_name="BROWNSUGAR"

test_mode = True

test_exchange_index=0
prod_exchange_hostname="production"

class Stock:
    def __init__(self):
        self.lowestsell = 0
        self.highestbuy = 0
        self.fair = 0.0
        self.hasSeen = False
        self.hasHigh = False
        self.hasLow = False

class Stocks:
    def __init__(self):
        self.dict = {}
        self.dict['BOND'] = Stock()
        self.dict['BABZ'] = Stock()
        self.dict['BABA'] = Stock()
        self.dict['AAPL'] = Stock()
        self.dict['MSFT'] = Stock()
        self.dict['GOOG'] = Stock()
        self.dict['XLK'] = Stock()



port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    x = exchange.readline()
    return json.loads(x)
    

def getlowsell(arr):
    lowest = 1000000
    for x in arr:
        lowest = min(lowest, x[0])
    return lowest

def gethighbuy(arr):
    highest = -100
    for x in arr:
        highest = max(highest, x[0])
    return highest

def main():
    count = 1
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file= sys.stderr)

    usd = 0

    stocks = Stocks()
    xlk = 0
    time.sleep(10)
    
    while True:
        hello_from_exchange = read_from_exchange(exchange)
        d = hello_from_exchange
        if d['type'] == 'book':
            sellarr = d['sell']
            buyarr = d['buy']
            mystock = stocks.dict[d['symbol']]
            if d['symbol'] == 'BABA':
                if sellarr != []:
                    mystock.lowestsell = getlowsell(sellarr)
                if buyarr != []:
                    mystock.highestbuy = gethighbuy(buyarr)
            if d['symbol'] == 'BABZ':
                if sellarr != []:
                    mystock.lowestsell = getlowsell(sellarr)
                if buyarr != []:
                    mystock.highestbuy = gethighbuy(buyarr)
            if stocks.dict['BABA'].lowestsell < stocks.dict['BABZ'].lowestsell:
                count += 1
                write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABA', 'dir': 'BUY', 'price': stocks.dict['BABA'].lowestsell, 'size': 10})
                if stocks.dict['BABA'].highestbuy + 10 >= stocks.dict['BABZ'].highestbuy:
                    count += 1
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABA', 'dir': 'SELL', 'price': stocks.dict['BABA'].highestbuy, 'size': 10})
                else:
                    write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'BABA', 'dir': 'SELL', 'size': 10})
                    count += 1
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABZ', 'dir': 'SELL', 'price': stocks.dict['BABZ'].highestbuy, 'size': 10})
            else:
                count += 1
                write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABZ', 'dir': 'BUY', 'price': stocks.dict['BABZ'].lowestsell, 'size': 10})
                if stocks.dict['BABZ'].highestbuy + 10 >= stocks.dict['BABA'].highestbuy:
                    count += 1
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABZ', 'dir': 'SELL', 'price': stocks.dict['BABZ'].highestbuy, 'size': 10})
                else:
                    write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'BABZ', 'dir': 'SELL', 'size': 10})
                    count += 1
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BABA', 'dir': 'SELL', 'price': stocks.dict['BABA'].highestbuy, 'size': 10})    
        time.sleep(1)
'''     if d['type'] == 'fill':
            sze = d['size']
            price = d['price']
            if d['dir'] == 'BUY':
                usd -= price * sze
                xlk += 10
            elif d['dir'] == 'SELL':
                usd += price * sze
            elif d['dir'] == '':
                usd = 0
        if d['type'] == 'book':
            sellarr = d['sell']
            buyarr = d['buy']
            mystock = stocks.dict[d['symbol']]
            mystock.lowestsell = getlowsell(sellarr)
            mystock.highestbuy = gethighbuy(buyarr)
            mystock.fair = (mystock.lowestsell + mystock.highestbuy) / 2.0
            mystock.hasSeen = True
            print(d['symbol'])
            print(mystock.fair)
            print(mystock.lowestsell)
            print(mystock.highestbuy)
            print(d)
            print()
            if stocks.dict['AAPL'].hasSeen == False or stocks.dict['MSFT'].hasSeen == False or stocks.dict['GOOG'].hasSeen == False or stocks.dict['XLK'].hasSeen == False:
                print("NOT TRADING")
            else:
                if 3 * 1000 + 2 * stocks.dict['AAPL'].fair + 3 * stocks.dict['MSFT'].fair + 2 * stocks.dict['GOOG'].fair + 100 < stocks.dict['XLK'].fair * 10:
                    count += 1
                    print("SELL XLK")
                    write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'XLK', 'dir': 'SELL', 'size': 10})
                if 3 * 1000 + 2 * stocks.dict['AAPL'].fair + 3 * stocks.dict['MSFT'].fair + 2 * stocks.dict['GOOG'].fair + 100 > stocks.dict['XLK'].fair * 10 and xlk < 100:
                    count += 1
                    print("BUY XLK")
                    write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'XLK', 'dir': 'BUY', 'size': 10})
'''



if __name__ == "__main__":
    main()
