### Crypto Discord Bot ####
############################

# Import packages
import discord
from discord.ext import tasks
import numpy as np
import pandas as pd
from functions import get_available_coins, check_coin_selection, retrieve_marketdata, calculate_portfolio_performance
from motivational_quotes import quotes
from config import TOKEN, CHANNEL_ID

# Initialise client
client = discord.Client()

# Initialise available coins and portfolio storage data frame
available_coins = get_available_coins(sorting="market_cap")
portfolio_df = pd.DataFrame(columns=["Coins", "Amount", "Entry"])


#######################
# Set up recurring tasks
#######################

# Provides market update of the 10 highest capitalised coins
@tasks.loop(seconds=(1.5 * 60 * 60))  # 1.5 hour
async def market_update():
    # Retrieve coins with highest market capitalisation
    c_num = 10
    quote_coins = str(available_coins[:c_num]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

    # Prepare message and retrieve market data
    embed = discord.Embed(title=":new_moon: Market Update :new_moon:")
    embed = retrieve_marketdata(quote_coins, embed, sorting="market_cap")
    await client.get_channel(CHANNEL_ID).send(content=None, embed=embed)


# Returns hottest coins wrt to 1h % change on CoinMarketCap with stats
@tasks.loop(seconds=(0.5 * 60 * 60))  # 30 min
async def coinupdate():
    # Convert coins on watchlist into API format
    coins = str(relevant_coins).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

    # Prepare message and retrieve market data
    embed = discord.Embed(title=":money_mouth: Coin Watch Update :money_mouth:")
    embed = retrieve_marketdata(coins, embed, sorting="market_cap")
    await client.get_channel(CHANNEL_ID).send(content=None, embed=embed)


# Returns hottest coins wrt to 1h % change on CoinMarketCap with stats
@tasks.loop(seconds=(60 * 60))  # 1 hours
async def hottest():
    # Retrieve hottest coins
    c_num = 10
    quote_coins = str(get_available_coins(sorting='percent_change_1h')[:c_num]).replace("[", "").replace("]",
                                                                                                         "").replace(
        " ", "").replace("'", "")

    # Prepare message and retrieve market data
    embed = discord.Embed(title=":fire: Hottest Coins :fire:")
    embed = retrieve_marketdata(quote_coins, embed, sorting="percent_change_1h")
    await client.get_channel(CHANNEL_ID).send(content=None, embed=embed)


# Returns latest added coins on CoinMarketCap with stats
@tasks.loop(seconds=(6 * 60 * 60))  # 6 hours
async def latest():
    # Retrieve latest added coins
    c_num = 10
    latest_coins = get_available_coins(sorting='date_added')
    latest_coins.reverse()
    quote_coins = str(latest_coins[:c_num]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

    # Prepare message and retrieve market data
    embed = discord.Embed(title=":new: Latest Coins :new:")
    embed = retrieve_marketdata(quote_coins, embed, sorting="date_added")
    await client.get_channel(CHANNEL_ID).send(content=None, embed=embed)


#######################
# Bot Handling
#######################
@client.event
async def on_ready():
    # Start scheduled task
    market_update.start()
    hottest.start()
    latest.start()

    # Send welcome message
    embed = discord.Embed(title="Crypto Chris entered the chat",
                          description="I am here to support your crypto trading. I will provide frequent market updates and monitor your crypto portfolio. Send '!help' to learn more about my superpowers.")
    embed.set_image(url="https://assets.bwbx.io/images/users/iqjWHBFdfxIU/inMIjzOd7HHI/v0/1000x-1.jpg")
    await client.get_channel(CHANNEL_ID).send(content=None, embed=embed)


# Message handling
@client.event
async def on_message(message):
    # Get message content and author details
    mes = message.content
    author = message.author.id
    authorname = message.author.name

    # help routine returns functions manual
    if mes == "!help":
        # Prepare message
        embed = discord.Embed(title="Help on Crypto Chris", description="Some useful commands")
        embed.add_field(name="!help", value="returns all bot functions")
        embed.add_field(name="!motivation", value="cheers you up with a motivational crypto quote")
        embed.add_field(name="!watch", value="add coins to watchlist. Use command '!watch [coin1,coin2']")
        embed.add_field(name="!coinwatch", value="returns coins on watchlist")
        embed.add_field(name="!coinupdate", value="returns market update on watchlisted coins")
        embed.add_field(name="!quote",
                        value="returns latest market data for a list of coins. Use command '!quote [coin1,coin2]'")
        embed.add_field(name="!marketupdate",
                        value="provides market update for the X biggest capitalised coins. Use command '!marketupdate [X]'")
        embed.add_field(name="!hottest",
                        value="returns X hottest coins by 1h percentage change. Use command '!hottest [X]'")
        embed.add_field(name="!latest", value="returns X latest added coins. Use command '!latest [X]'")
        embed.add_field(name="!calc", value="returns calculation result. Use command '!calc [X*Y]'")
        embed.add_field(name="!portfolio",
                        value="add user's portfolio data in order to calculate the performance. Use command '!portfolio coins=[coin1, coin2] amount=[amount1, amount2] entry=[entry1,entry2]'")
        embed.add_field(name="!profit", value="returns user's portfolio performance")
        await message.channel.send(content=None, embed=embed)

    # motivaton routine returns motivational crypto quotes
    if mes == "!motivation":
        q_num = np.random.randint(0, len(quotes) - 1)
        await message.channel.send(quotes[q_num])

    # watch routine let's you add new coins to monitor
    if "!watch" in mes:
        # Assign relevant coins
        global relevant_coins
        relevant_coins = mes.replace("]", "").split("[")[1].split(",")

        # Convert coins into API format
        coins = str(relevant_coins).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

        # Check if coins are available to monitor
        coin_check = check_coin_selection(coins, available_coins)
        if coin_check == "Success":
            embed = discord.Embed(title="Coin Watch",
                                  description="***" + str(relevant_coins).replace("[", "").replace("]",
                                                                                                   "") + "*** are now monitored. Extreme gains inbound")
            coinupdate.start()
        else:
            embed = discord.Embed(title="Error Coin Watch",
                                  description="An error occurred! ***" + str(coin_check).replace("[", "").replace("]",
                                                                                                                  "") + "***  is/are not available at CoinMarketCap. Please resubmit monitoring request")
        await message.channel.send(content=None, embed=embed)

    # coinwatch routine returns monitored coins
    if mes == "!coinwatch":
        try:
            if len(relevant_coins) == 0:
                embed = discord.Embed(title="Coin Watch",
                                      description="Currently I am not monitoring any coins. Use command '!watch' to add coins")
            else:
                embed = discord.Embed(title="Coin Watch",
                                      description="Currently " + str(relevant_coins).replace("[", "").replace("]",
                                                                                                              "") + " are monitored. Use command '!watch' to add more coins")
        except:
            embed = discord.Embed(title="Coin Watch",
                                  description="Currently not monitoring any coins. Use command '!watch' to add coins")
        await message.channel.send(content=None, embed=embed)

    # coinupdate routine returns live crypto market update for monitored coins
    if mes == "!coinupdate":
        # Convert coins into API format
        coins = str(relevant_coins).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

        # Prepare message and retrieve market data
        embed = discord.Embed(title=":money_mouth: Coin Watch Update :money_mouth:")
        embed = retrieve_marketdata(coins, embed, sorting="market_cap")
        await message.channel.send(content=None, embed=embed)

    # quote routine let's you get the data for specific coins
    if "!quote" in mes:
        # Get coin to retrieve quote
        quote_coins = mes.split("[")[1].replace(" ", "").replace("]", "")

        # Check if coins are available and retrieve market data
        coin_check = check_coin_selection(quote_coins, available_coins)
        if coin_check == "Success":
            embed = discord.Embed(title=":money_mouth: Latest Quotes :money_mouth:")
            embed = retrieve_marketdata(quote_coins, embed, sorting="market_cap")
        else:
            embed = discord.Embed(title="Error Quote Request",
                                  description="An error occurred! ***" + str(coin_check).replace("[", "").replace("]",
                                                                                                                  "") + "***  is/are not available at CoinMarketCap. Please resubmit quote request")
        await message.channel.send(content=None, embed=embed)

    # market update routine provides a crypto market overview
    if "!marketupdate" in mes:
        # Get number of coins and coins
        c_num = int(mes.split("[")[1].replace("]", ""))
        quote_coins = str(available_coins[:c_num]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

        # Prepare message and retrieve market data
        embed = discord.Embed(title=":new_moon: Market Update :new_moon:")
        embed = retrieve_marketdata(quote_coins, embed, sorting="market_cap")
        await message.channel.send(content=None, embed=embed)

    # hottest routine provides an overview of the hottest coins measured by 1h percentage change
    if "!hottest" in mes:
        # Get number of coins and coins
        c_num = int(mes.split("[")[1].replace("]", ""))
        quote_coins = str(get_available_coins(sorting='percent_change_1h')[:c_num]).replace("[", "").replace("]",
                                                                                                             "").replace(
            " ", "").replace("'", "")

        # Prepare message and retrieve market data
        embed = discord.Embed(title=":fire: Hottest Coins :fire:")
        embed = retrieve_marketdata(quote_coins, embed, sorting="percent_change_1h")
        await message.channel.send(content=None, embed=embed)

    # hottest routine provides an overview of the hottest coins measured by 1h percentage change
    if "!latest" in mes:
        # Get number of coins and coins
        c_num = int(mes.split("[")[1].replace("]", ""))
        latest_coins = get_available_coins(sorting='date_added')
        latest_coins.reverse()
        quote_coins = str(latest_coins[:c_num]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")

        # Prepare message and retrieve market data
        embed = discord.Embed(title=":new: Latest Coins :new:")
        embed = retrieve_marketdata(quote_coins, embed, sorting="date_added")
        await message.channel.send(content=None, embed=embed)

    # calc routine to run simple calculations in discord chat
    if "!calc" in mes:
        # Run calculations
        calculations = mes.split("[")[1].replace("]", "")
        result = eval(calculations)

        # Return message with result
        await message.channel.send(content=result, embed=None)

    # portfolio routine to set up portfolio data that can be used to monitored performance
    if "!portfolio" in mes:
        # Retrieve portfolio data
        port_coins = (mes.split("[")[1].split("]")[0]).replace(" ", "").split(",")
        port_amount = list(map(float, (mes.split("[")[2].split("]")[0]).replace(" ", "").split(",")))
        port_entry = list(map(float, ((mes.split("[")[3].split("]")[0]).replace(" ", "").split(","))))

        # Check if coins in portfolio are available
        coin_check = check_coin_selection(port_coins, available_coins)
        if coin_check == "Success":
            # Add portfolio to portfolio_df
            portfolio_df.loc[author, :] = [port_coins, port_amount, port_entry]
            embed = discord.Embed(title=":moneybag: Details were added to your portfolio " + authorname + " :moneybag:")
        else:
            embed = discord.Embed(title="Error Portfolio Request",
                                  description="An error occurred! ***" + str(coin_check).replace("[", "").replace("]",
                                                                                                                  "") + "***  is/are not available at CoinMarketCap. Please resubmit portfolio request")
        await message.channel.send(content=None, embed=embed)

    # profit routine to calculate performance for user's portfolio
    if mes == "!profit":
        # Calculate portfolio performance and return message
        if author in portfolio_df.index:
            port_data = portfolio_df.loc[author, :]
            embed = discord.Embed(title=":clown: {}'s Performance :clown:".format(authorname))
            embed = calculate_portfolio_performance(port_data, embed)
        else:
            embed = discord.Embed(
                title=":clown: No Portfolio for {} found. Please submit the '!portfolio' command first :clown:".format(
                    authorname))
        await message.channel.send(content=None, embed=embed)


# Start client
client.run(TOKEN)
