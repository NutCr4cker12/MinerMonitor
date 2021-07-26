from datetime import datetime
from src.Monitors import create_client
from Config import Config

def get_active_hours(payouts, unpaid):
    """
        payouts: { list: [ { created }]} -- From NiceHash Api 
        unpaid: { data: [time] } -- From NiceHash Api

        returns payouts[list] sorted by time (ascending) and filled with mining_start and mining_end fields
    """
    unpaid_data = unpaid["data"]
    payout_data = payouts["list"]

    # Sort by ascending time
    unpaid_data.reverse()
    payout_data.reverse()

    prev_timestamp = unpaid_data[0][0] - 60 * 1000
    for payout in payout_data:
        payout_time = payout["created"]

        if payout["currency"]["enumName"] != "BTC":
            raise Exception("Got paid in something else than BTC ?! ", payout)

        # Filtering unpaid based on index is sufficient enough
        unpaid_filtered = list(filter(lambda x: x[0] > prev_timestamp and x[0] <= payout_time, unpaid_data))
        print(len(unpaid_filtered))
        payout["mining_start"] = unpaid_filtered[0][0]
        payout["mining_end"] = unpaid_filtered[-1][0]

        # Update previous timestamp
        prev_timestamp = payout_time
        
    return payout_data

def history(start: datetime, end: datetime):
    options = Config(production=False)
    nh_api = create_client(options.nicehashApi)
    
    # Get rig payments
    payouts = nh_api.get_my_payouts(start, end)

    # Get algo stats
    # TODO NiceHash keeps only last 7 days worth of data stored !!!
    unpaid = nh_api.get_unpaid(start, end)

    # Fill mining start and end times
    payout_list = get_active_hours(payouts, unpaid)

    # Match BTC price

    # Remember to keep account on the WEIGHTS and RATE LIMITS !
    # Currently 1,200 weighted request per minute
    # r.headers["x-mbx-used-weight-1m"]
    # The current ratelimits can be get from "https://api.binance.com/api/v3/exchangeInfo" ["rateLimits"]
    #       exchangeInfo has a weight of 10 and aggTrades weight of 1 (at 2021-06-14)

    # Match power consumption

    # HardCode previous, non-monitored data
    # 2070 + CPU from start - until 3090 received saturday night
    #       => 0.35 kWh
    #
    # Check out the mining rate / history stats from nicehash (or just until the extention cord from jimms)
    #       => only 3090 at the beginning => 350 + 110 = 0.41 kWh
    #
    # Check out / keep an eye out of historical power mode stat ??
    #
    # Date of extention cord from Jimms
    #       => prob 3090 + 2070 both full => 350 + 170 + 110 = 0.63 kWh
    #
    # AfterBurner downloaded at 2021-05-13
    #       => reduced to current => 270 + 125 + 110 = 515 kWh

    return payout_list
