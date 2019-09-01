# tmb - Library for TMB API


Use this library to interact with the TMB (Transports Metropolitans de Barcelona) API.



## Functionality 
It supports the following services
- iBus (get remain minutes for a given stop and line)



## Generate API keys

* Go to [developer.tmb.cat](https://developer.tmb.cat/).
* Login using your personal account.
* Create a [new application](https://developer.tmb.cat/account/applications), call it as you want.
* Once created, you will see two variables: `APP_ID` and `APP_KEY`. 



## Example

### iBus

Create the iBus object using the API keys generated from TMB portal.

```
from tmb import IBus

ibus = IBus(APP_ID, APP_KEY)
forecast = ibus.get_stop_forecast('1265','V19')
print(f"{forecast} mins")
```



## Projects Depending on `tmb`

https://github.com/home-assistant/home-assistant