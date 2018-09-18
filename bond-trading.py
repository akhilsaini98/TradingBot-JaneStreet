import sys
import socket
import json
import time

team_name="BROWNSUGAR"

test_mode = False

test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    print("connected to: " + exchange_hostname + " " + str(port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

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

    
    while True:
        count = count + 1
        write_to_exchange( exchange,   {"type": "add", "order_id": count, "symbol": "BOND", "dir": "BUY", "price": 998, "size": 15} )
        count = count + 1

        write_to_exchange( exchange,   {"type": "add", "order_id": count, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 15} )
        # hello_from_exchange = read_from_exchange(exchange)
       # print(hello_from_exchange)
        time.sleep(1)


if __name__ == "__main__":
    main()
