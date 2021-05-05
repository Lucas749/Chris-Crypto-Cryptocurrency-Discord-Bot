# Chris-Crypto-Cryptocurrency-Discord-Bot
Chris Crypto is a discord bot that provides crypto market updates and let's you monitor coins and your portfolio. Market data is downloaded from CoinMarketCap via their [API](https://coinmarketcap.com/api/).

<p align="center">
  <img  width="308" height="520" src="https://github.com/Lucas749/Chris-Crypto-Cryptocurrency-Discord-Bot/blob/master/Demonstration/Chris%20Crypto%20Demo.gif">
</p>

# File Overview
1. bot.py - Main discord bot handling
2. functions.py - Provides functions used by the bot (e.g. downloading market data)
3. config.py - Provides relevant keys and tokens
4. motivational_quotes.py - Provides cryptocurrency related quotes

# Chris Crypto's Functions
**!help:** returns all bot functions \
**!motivation** cheers you up with a motivational crypto quote \
**!watch** add coins to watchlist. Use command '!watch [coin1,coin2]' \
**!coinwatch** returns coins on watchlist \
**!coinupdate** returns market update on watchlisted coins \
**!quote** returns latest market data for a list of coins. Use command '!quote [coin1,coin2]' \
**!marketupdate** provides market update for the X biggest capitalised coins. Use command '!marketupdate [X]' \
**!hottest** returns X hottest coins by 1h percentage change. Use command '!hottest [X]' \
**!latest** returns X latest added coins. Use command '!latest [X]' \
**!calc** returns calculation result. Use command '!calc [X*Y]' \
**!portfolio** add user's portfolio data in order to calculate the performance. Use command '!portfolio coins=[coin1, coin2] amount=[amount1, amount2] entry=[entry1,entry2]' \
**!profit** returns user's portfolio performance
