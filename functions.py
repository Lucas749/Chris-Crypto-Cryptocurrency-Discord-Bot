#### Functions for Crypto Discord Bot ####
##########################################

# Import packages
from coinmarketcapapi import CoinMarketCapAPI
import pandas as pd


# Retrieve all available coins from CoinMarketCap
def get_available_coins(sorting="market_cap"):
    # Initialise CMC AP
    from config import API_KEY
    cmc = CoinMarketCapAPI(API_KEY)

    # Retrieve CMC data
    r_latest = cmc.cryptocurrency_listings_latest(cryptocurrency_type="all", limit=5000, sort=sorting, sort_dir="desc")

    # Get all coins
    coins_list = []
    for c in r_latest.data:
        symbol = c['symbol']
        coins_list.append(symbol)
    return coins_list


# Check if selected coins are available on CoinMarketCap and returns unavailable coins
def check_coin_selection(coins, available_coins, update_coin_list=True):
    # Convert str item to list if necessary
    if type(coins) == str:
        coins = str(coins).replace("[", "").replace(" ", "").replace("]", "").replace("'", "").split(",")

    # Determine unavailable coins
    unavailable_coins = []
    for c in coins:
        if c not in available_coins:
            unavailable_coins.append(c)
    if len(unavailable_coins) == 0:
        return "Success"
    else:
        if update_coin_list:
            # Update available coins if coin not in previously gathered coin data
            available_coins = get_available_coins()
            check_coin_selection(coins, available_coins, update_coin_list=False)
        return unavailable_coins


# Retrieves latest market data from CoinMarketCap and returns embed object
def retrieve_marketdata(coins, embed, sorting="market_cap"):
    # Initialise CMC API
    from config import API_KEY
    cmc = CoinMarketCapAPI(API_KEY)

    # Retrieve CMC data
    r_latest = cmc.cryptocurrency_quotes_latest(symbol=coins)

    # Generate dataframe
    dict_keys = r_latest.data.keys()
    df_empty = pd.DataFrame()

    # Unpack dictionary
    for k in dict_keys:
        data = r_latest.data[k]
        temp = data.copy()
        temp_quote = data['quote']['USD']
        temp.pop('quote')
        temp.pop('platform')
        df_temp = pd.DataFrame.from_dict(temp, orient='index').T
        df_temp_quote = pd.DataFrame.from_dict(temp_quote, orient='index').T
        df_temp = pd.concat([df_temp, df_temp_quote], axis=1)
        df_empty = df_empty.append(df_temp)
    df_empty.index = df_empty.name

    # Sort df
    df_empty.sort_values(by=sorting, ascending=False, inplace=True)

    # Add coins to message
    for name in df_empty.index:
        symbol = df_empty.loc[name, 'symbol']
        price = df_empty.loc[name, 'price']
        date_added = pd.to_datetime(df_empty.loc[name, 'date_added']).date().strftime('%d-%m-%Y')
        volume_24h = "{:,.2f}".format(df_empty.loc[name, 'volume_24h'])
        last_updated = df_empty.loc[name, 'last_updated'][0]
        market_cap = "{:,.2f}".format(df_empty.loc[name, 'market_cap'])
        circulating_supply = "{:,.2f}".format(df_empty.loc[name, 'circulating_supply'])
        percent_change_1h = "{:,.2f}".format(df_empty.loc[name, 'percent_change_1h'])
        percent_change_24h = "{:,.2f}".format(df_empty.loc[name, 'percent_change_24h'])
        percent_change_7d = "{:,.2f}".format(df_empty.loc[name, 'percent_change_7d'])
        percent_change_30d = "{:,.2f}".format(df_empty.loc[name, 'percent_change_30d'])
        percent_change_60d = "{:,.2f}".format(df_empty.loc[name, 'percent_change_60d'])
        percent_change_90d = "{:,.2f}".format(df_empty.loc[name, 'percent_change_90d'])
        embed.add_field(name=name + " (" + symbol + ")", value="**Last Updated:** {} \n \
            **Date Added:** {} \n \
           **Price:** {} \n \
           **Volume 24h:** {} \n \
           **Market Cap:** {} \n \
           **Circulating Supply:** {} \n \
           **% 1h:** {} \n \
            **% 24h:** {} \n \
            **% 7d:** {} \n \
            **% 30d:** {} \n \
            **% 60d:** {} \n \
            **% 90d:** {}".format(last_updated, date_added, price, volume_24h, market_cap, circulating_supply,
                                  percent_change_1h,
                                  percent_change_24h, percent_change_7d, percent_change_30d, percent_change_60d,
                                  percent_change_90d))
    return embed


# Calculates performance of individual user portfolios
def calculate_portfolio_performance(port_data, embed):
    # Initialise CMC API
    from config import API_KEY
    cmc = CoinMarketCapAPI(API_KEY)

    # Retrieve data from portfolio dataframe
    coins = str(port_data["Coins"]).replace("[", "").replace(" ", "").replace("]", "").replace("'", "")
    amount = port_data["Amount"]
    entry = port_data["Entry"]

    # Retrieve CMC data
    r_latest = cmc.cryptocurrency_quotes_latest(symbol=coins)

    # Generate dataframe
    dict_keys = r_latest.data.keys()
    df_empty = pd.DataFrame()

    # Unpack dictionary
    for k in dict_keys:
        data = r_latest.data[k]
        temp = data.copy()
        temp_quote = data['quote']['USD']
        temp.pop('quote')
        temp.pop('platform')
        df_temp = pd.DataFrame.from_dict(temp, orient='index').T
        df_temp_quote = pd.DataFrame.from_dict(temp_quote, orient='index').T
        df_temp = pd.concat([df_temp, df_temp_quote], axis=1)
        df_empty = df_empty.append(df_temp)
    df_empty.index = df_empty.name

    # Sort df
    df_empty.sort_values(by="market_cap", ascending=False, inplace=True)

    # Add performance to message
    for name in df_empty.index:
        symbol = df_empty.loc[name, 'symbol']
        current_price = df_empty.loc[name, 'price']
        last_updated = df_empty.loc[name, 'last_updated'][0]
        pos_coin = port_data["Coins"].index(symbol)
        entry_price = entry[pos_coin]
        amount_coin = amount[pos_coin]
        profit_perc = "{:,.2f}".format(100 * (current_price / entry_price - 1))
        profit_abs = "{:,.2f}".format(entry_price * amount_coin * (current_price / entry_price - 1))
        date_added = pd.to_datetime(df_empty.loc[name, 'date_added']).date().strftime('%d-%m-%Y')
        volume_24h = "{:,.2f}".format(df_empty.loc[name, 'volume_24h'])
        percent_change_1h = "{:,.2f}".format(df_empty.loc[name, 'percent_change_1h'])
        percent_change_24h = "{:,.2f}".format(df_empty.loc[name, 'percent_change_24h'])
        embed.add_field(name=name + " (" + symbol + ")", value="**Last Updated:** {} \n \
            **Price:** {} \n \
            **Entry Price:** {} \n \
            **Profit %:** {} \n \
            **Profit Abs:** {} \n \
            **Date Added:** {} \n \
            **Volume 24h:** {} \n \
            **% 1h:** {} \n \
            **% 24h:** {}".format(last_updated, current_price, entry_price, profit_perc, profit_abs, date_added,
                                  volume_24h, percent_change_1h, percent_change_24h))
    return embed
