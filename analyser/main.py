import pandas as pd
import requests
import time
import json
import datetime

def web_get(url):
    status_code = 0
    nb_try = 0
    max_try = 3
    
    while status_code != 200 and nb_try < max_try:
        time.sleep(0.30)
        r = requests.get(url)
        status_code = r.status_code
        nb_try += 1
        if status_code != 200 and nb_try < max_try:
            print('Error {code} while loading {url}'.format(code=status_code, url=url))
            time.sleep(3)
    if status_code != 200:
        print('Skip {url}'.format(url=url))
    
    return json.loads(r.text)
        

class Transaction:
    
    def __init__(self, hash, sender=None, recipient=None, value=None, timestamp=None, block=None):
        self.hash = hash
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.timestamp = timestamp
        self.block = block

    @property
    def hash(self):
        return self._hash
    
    @hash.setter
    def hash(self, hash):
        if hash is None:
            self._hash = hash
        else:
            self._hash = hash.lower()

    @property
    def recipient(self):
        if self._recipient is None:
            self._populate()
        return self._recipient

    @recipient.setter
    def recipient(self, recipient):
        if recipient is None:
            self._recipient = recipient
        else:
            self._recipient = recipient.lower()

    @property
    def sender(self):
        if self._sender is None:
            self._populate()
        return self._sender

    @sender.setter
    def sender(self, sender):
        if sender is None:
            self._sender = sender
        else:
            self._sender = sender.lower()

    @property
    def value(self):
        if self._value is None:
            self._populate()
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = int(value, 0)

    @property
    def timestamp(self):
        if self._timestamp is None:
            self._populate_timestamp()
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        if timestamp is None:
            self._timestamp = timestamp
        else:
            self._timestamp = datetime.datetime.fromtimestamp(int(timestamp))
    
    @property
    def block(self):
        if self._block is None:
            self._populate()
        return self._block

    @block.setter
    def block(self, block):
        if block is None:
            self._block = block
        else:
            self._block = int(block, 0)

    def _populate(self):
        url = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={hash}'.format(hash=self.hash)
        data = web_get(url)
        self.sender = data['result']['from']
        self.recipient = data['result']['to']
        self.value = data['result']['value']
        self.block = data['result']['blockNumber']

    def _populate_timestamp(self):
        url = 'https://api.etherscan.io/api?module=block&action=getblockreward&blockno={block}'.format(block=self.block)
        data = web_get(url)
        self.timestamp = data['result']['timeStamp']

class Wallet:
    
    def __init__(self, address):
        self.address = address
        self._transactions = None
        self._balance = None

    @property
    def address(self):
        return self._addresss

    @address.setter
    def address(self, address):
        self._addresss = address.lower()

    @property
    def transactions(self):
        if self._transactions is None:
            self._populate_transactions()
        return self._transactions

    @property
    def balance(self):
        if self._balance is None:
            self._populate_balance()
        return self._balance

    def transactions_range(self, before=None, after=None, direction=None):
        if before is None:
            before = 99999999
        if after is None:
            after = 0
        if direction not in ['IN', 'OUT', 'ALL']:
            direction = 'ALL'
        
        for tx in self.transactions:
            if tx.block > after and tx.block < before:
                if direction == 'ALL':
                    yield tx
                elif direction == 'IN' and tx.recipient == self.address:
                    yield tx
                elif direction == 'OUT' and tx.sender == self.address:
                    yield tx
                    
    
    def _populate_transactions(self):
        # TODO: handle when more than ten thousands transactions
        url = 'http://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc'.format(address=self.address)
        data = web_get(url)
        self._transactions = list()
        for tx in data['result']:
            self._transactions.append(Transaction(
                hash=tx['hash'],
                sender=tx['from'],
                recipient=tx['to'],
                value=tx['value'],
                timestamp=tx['timeStamp'],
                block=tx['blockNumber']
            ))
        
        # sort in chronological order
        self._transactions.sort(key=lambda tx: tx.timestamp)
        
    def _populate_balance(self):
        url = 'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest'.format(address=self.address)
        data = web_get(url)
        self._balance = data['result']


if __name__ == '__main__':
    
    tx = Transaction('0x40eb908387324f2b575b4879cd9d7188f69c8fc9d87c901b9e2daaea4b442170')

    print(tx.sender.transactions_range(direction='OUT')[0].recipient.address)
    print(tx.recipient)
    print(tx.value)
    print(tx.timestamp)
    print(tx.block)

    wallet = Wallet('0xdD5e52c3f4075153159743D30Fba75f3A0a1424a')

    print(wallet.balance)
    for tx in wallet.transactions:
        print(tx.hash)
        break
    for tx in wallet.transactions_range(direction='OUT', after=7363716):
        print(tx.hash)
        break
