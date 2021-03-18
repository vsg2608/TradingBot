"""
    Below class is User manager and auth management
"""

"""Imports"""

from binance.client import Client,BinanceAPIException

"""Imports"""

"""User instance class"""
class User:  
    username= None
    password= None
    __apiKey= None
    ___apiSecret= None
    __authenticated= False
    client= None

    def __init__(self, api_key, api_secret):
        self.__apiKey= api_key
        self.___apiSecret= api_secret

    def authenticate(self):
        try:
            self.client = Client(self.__apiKey, self.___apiSecret, {"verify": False, "timeout": 20})
            self.__authenticated= True
        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)
            return False

        return True

    def isAuthenticated(self):
        try:
            if(self.__authenticated):
                self.client.ping()
                print('***** User: Authenticated *****')
                return True
            else:
                print('***** User: Not Authenticated *****')
                return False
        except BinanceAPIException as e:
            self.__authenticated= False
            print(e.status_code)
            print(e.message)
            return False
        return self.__authenticted

    def checkServerStatus(self):
        try:
            response = self.client.get_system_status()
            if ('status' in response and response['status'] == 0):
                print('***** Server Status: Normal *****')
                return True
            else:
                print('***** Server Status: System maintenance *****')
                return False
        except BinanceAPIException as e:
            self.__authenticated= False
            print(e.status_code)
            print(e.message)
            return False
        
    def checkAccountStatus(self):
        try:
            response = self.client.get_account_status()
            if ('msg' in response and response['msg'] == 'Normal'):
                print('***** Account Status: Normal *****')
                return True
            else:
                print('***** Account Status: Inactive *****')
                return False
        except BinanceAPIException as e:
            self.__authenticated= False
            print(e.status_code)
            print(e.message)
            return False
        
    def getUserAccountBalance(self):
        pass

    
