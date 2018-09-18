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

class Stocks:
    def __init__(self):
        self.dict = []
        self.dict['BOND'] = Stock()
        self.dict['BABZ'] = Stock()
        #self.dict[''] = Stock()
        #self.dict[] = Stock()
        #self.dict[] = Stock()



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
    try:
        x = exchange.readline()
        return json.loads(x)
    except:
        return {'type': 'error'}

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
    buyfor = 999
    sellfor = 1001
    buys = 0
    sells = 0
    buybulk = 15
    sellbulk = 15
    
    while True:
        if usd > -25000 & buys - sells < 100:
            count = count + 1
            if count % 2 == 0:
                count += 1
            write_to_exchange( exchange,   {"type": "add", "order_id": count, "symbol": "BOND", "dir": "BUY", "price": buyfor, "size": buybulk} )
            buys += buybulk
        if buys - sells > -100:
            count = count + 1
            if count % 2 != 0:
                count += 1
            write_to_exchange( exchange,   {"type": "add", "order_id": count, "symbol": "BOND", "dir": "SELL", "price": sellfor, "size": sellbulk} )
            sells += sellbulk

        hello_from_exchange = read_from_exchange(exchange)
        d = hello_from_exchange
        if d['type'] == 'fill':
            varx = d['size']
            orderid = d['order_id']
            if orderid % 2 == 0:
                usd += sellfor * varx
                sells -= varx
            else:
                usd -= buyfor * varx
                buys -= varx

        



if __name__ == "__main__":
    main()
