# 👋🏻 Introduction

### If you like this pls give me a star 🙏
### i Recomand hosting your self since there is multiple people using vercel which makes it slower so uh yeah pls host it ur self it will be more faster
### im planing to Make a premium one which will update realtime no delays and reliable but this will require 5 dollar for lifetime to Maintain the Hosting
### [CHANGELOGS](https://github.com/Just3itx/Grow-A-Garden-API/blob/main/CHANGELOG.md)

Welcome to the **Grow a Garden API**. This open-source API provides a straightforward way to access in-game gardening data—including stock levels, weather conditions, and item information—without the need to host or maintain bots yourself.

It uses the **Vulcan API** to gather all relevant information in real-time, eliminating the need for users to run and manage bots that stay AFK in the game. The API also supports real-time restock updates, ensuring you always have the most current data.

features include:
- Access to in-game gardening stock data using the Vulcan API.
- Retrieval of current weather conditions relevant to the game.
- Detailed item information available through the API.
- Real-time restock notifications as they occur.
- Fully open-source and available for community use and contribution.

# 💿Too Lazy to host your self?
Don't Worry i've decided to use Vercel to host this api so u don't have to here is the url
- https://growagardenapi.vercel.app/api/stock/GetStock
- https://growagardenapi.vercel.app/api/GetWeather
- https://growagardenapi.vercel.app/api/Item-Info
- https://growagardenapi.vercel.app/api/stock/Restock-Time
- https://growagardenapi.vercel.app/api/CalculatePrice?Name=Carrot&Weight=.25&Variant=Rainbow&Mutation=Moonlit,Bloodlit,Disco

# ⚙️ Installation

To get started with the Grow a Garden API, you’ll need to have Node.js installed. After that, you can set up the API with the following dependencies:

```bash
npm install express fs path os blessed
```

# 💻 Running the Server

Once your setup is complete, you can start the server by running:

```bash
node server.js
```

This will launch the API server and make it ready to handle requests.

# 📋 Upcoming Features
- Caclulator for Pets | This would allow u to see how much your pet is worth in Sheckles
- ~~Calculator that calculate plant value with the weight and mutations~~
- Host Bot | This can allow you to host an actual bot to afk and collect the Data
- Other random features to be discovered by my brain 
