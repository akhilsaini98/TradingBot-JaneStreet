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
        self.hasBuy = False
        self.hasSell = False
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
    return json.loads(exchange.readline())

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
    
    while True:
        hello_from_exchange = read_from_exchange(exchange)
        d = hello_from_exchange
        if d['type'] == 'reject':
            print('error:', d)
        if d['type'] == 'ack':
            print('ack:', d)
        if d['type'] == 'book':
            sellarr = d['sell']
            buyarr = d['buy']
            mystock = stocks.dict[d['symbol']]
            mystock.lowestsell = getlowsell(sellarr)
            mystock.highestbuy = gethighbuy(buyarr)
            mystock.fair = int((mystock.lowestsell + mystock.highestbuy) / 2.0)
            mystock.hasSeen = True
            if sellarr != []:
                mystock.hasSell = True
            else:
                mystock.hasSell = False
            if buyarr != []:
                mystock.hasBuy = True
            else:
                mystock.hasBuy = False
        
            if stocks.dict['AAPL'].hasBuy == True and stocks.dict['MSFT'].hasBuy == True and stocks.dict['GOOG'].hasBuy == True and stocks.dict['XLK'].hasBuy == True and stocks.dict['AAPL'].hasSell == True and stocks.dict['MSFT'].hasSell == True and stocks.dict['GOOG'].hasSell == True and stocks.dict['XLK'].hasSell == True:
                #print()
                #print(d['symbol'])
                #print(mystock.fair)
                #print(mystock.lowestsell)
                #print(mystock.highestbuy)
                #print(d)

                if 3 * 1000 + 2 * stocks.dict['AAPL'].fair + 3 * stocks.dict['MSFT'].fair + 2 * stocks.dict['GOOG'].fair > (stocks.dict['XLK'].fair * 10) + 100:
                    count += 1
                    print("SELL XLK")
                    print('SELL GOOG:', count, stocks.dict['GOOG'].fair)
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'GOOG', 'dir': 'SELL', 'price' : stocks.dict['GOOG'].fair, 'size': 2})
                    count += 1
                    print('SELL MSFT:', count)
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'MSFT', 'dir': 'SELL', 'price' : stocks.dict['MSFT'].fair, 'size': 3})
                    count += 1
                    print('SELL AAPL:', count)
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'AAPL', 'dir': 'SELL', 'price' : stocks.dict['AAPL'].fair, 'size': 2})
                    count += 1
                    print('SELL BOND:', count)
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BOND', 'dir': 'SELL', 'price' : stocks.dict['BOND'].fair, 'size': 3})
                    count += 1
                    print('BUY XLK:', count)
                    write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'XLK', 'dir': 'BUY', 'price' : stocks.dict['XLK'].fair, 'size': 10})
                    count += 1
                    print('CONVERT:', count)
                    write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'XLK', 'dir': 'SELL', 'size': 10})
                
                elif 3 * 1000 + 2 * stocks.dict['AAPL'].fair + 3 * stocks.dict['MSFT'].fair + 2 * stocks.dict['GOOG'].fair + 100 < stocks.dict['XLK'].fair * 10:
                        count += 1
                        print("BUY XLK")
                        write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'XLK', 'dir': 'SELL', 'price' : stocks.dict['XLK'].fair, 'size': 10})
                        count += 1
                        write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'GOOG', 'dir': 'BUY', 'price' : stocks.dict['GOOG'].fair, 'size': 2})
                        count += 1
                        write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'MSFT', 'dir': 'BUY', 'price' : stocks.dict['MSFT'].fair, 'size': 3})
                        count += 1
                        write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'AAPL', 'dir': 'BUY', 'price' : stocks.dict['AAPL'].fair, 'size': 2})
                        count += 1
                        write_to_exchange(exchange, {'type': 'add', 'order_id': count, 'symbol': 'BOND', 'dir': 'BUY', 'price' : stocks.dict['BOND'].fair, 'size': 3})
                        count += 1
                        write_to_exchange(exchange, {'type': 'convert', 'order_id': count, 'symbol': 'XLK', 'dir': 'BUY', 'size': 10})
                    
        #time.sleep(0.001)



if __name__ == "__main__":
    main()
