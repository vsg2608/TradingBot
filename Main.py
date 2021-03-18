import urllib3, json
urllib3.disable_warnings() # Removing https warnings from urllib3 as binace certificates are not installed

#Custom files
import Constants as constants
from UserManager import User
from Bot import Bot

#%% Read configuration for bot

with open('configuration.json') as f:
    configuration = json.load(f)

#%%
user= User(constants.API_KEY,constants.API_SECRET)
user.authenticate()

#%%


if(user.isAuthenticated() and user.checkServerStatus() ): #user.checkAccountStatus()
    
    print('\n User Authenticated and ready for trading \n Please select the symbol you want to trade:')
    itr=1
    confMap={}
    for key in configuration:
        print('%s\t%s'%(itr,key))
        confMap[itr]= configuration[key]
        itr+=1
    
    response= int(input())
    
    if response < itr and response in confMap:
        bot= Bot(user.client, confMap[response])
        bot.start()
