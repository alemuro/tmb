# tmb - Python library for TMB API

![build](https://img.shields.io/github/workflow/status/alemuro/tmb/Main) ![downloads](https://img.shields.io/pypi/dm/tmb) ![version](https://img.shields.io/pypi/v/tmb)

Library to interact with the TMB (Transports Metropolitans de Barcelona) API.

Currently it supports the following TMB services:
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