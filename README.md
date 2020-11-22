![Main](https://github.com/alemuro/tmb/workflows/Main/badge.svg)

# tmb - Library for TMB API


Use this library to interact with the TMB (Transports Metropolitans de Barcelona) API.



## Functionality 
It supports the following services
- iBus (get remain minutes for a given stop and line)
- Planner (Get list of itineraries to go from `from_coords` to `to_coords`)

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

### Planner

Create the Planner object using the API keys generated from TMB portal.

```
from tmb import Planner

planner = Planner(APP_ID, APP_KEY)
plans = planner.get_itineraries('41.3755204,2.1498870', '41.3878951,2.1308587')
print(plans)
```



## Projects Depending on `tmb`

https://github.com/home-assistant/home-assistant