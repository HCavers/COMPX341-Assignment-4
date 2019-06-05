import time
import redis
import re
from flask import Flask
from math import sqrt
from itertools import count, islice

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def check_prime(num):
    n = int(num,10)
    if n  < 2:
        return False

    for number in islice(count(2), int(sqrt(n)-1)):
        if n % number == 0:
            return False

    return True

def save_num(num):
    cache.sadd('Primes', num)


def convert_to_num(value):
    line = re.sub("[^0-9]", "", value)
    return line

@app.route('/hello')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

@app.route('/isPrime/<number>')
def isPrime(number):
    if check_prime(number):
         save_num(number)
         return '{} is a prime.\n'.format(number)
    else:
         return '{} is not a prime.\n'.format(number)

@app.route('/primeStored')
def primesStored():
    line = ''
    primes = cache.smembers('Primes') 
    for value in primes:
        line += convert_to_num(str(value)) + ' '
    line += '\n'
    return line
