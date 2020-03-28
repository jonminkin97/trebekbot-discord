# TrebekBot for Discord
A Discord bot to play an endless game of jeopardy.


## Setup
### Registrering a bot on Discord
The first step is to go to the [Discord Developer Portal](https://discordapp.com/developers/applications) and register a new application.

Once you have created the application, go to the pane on the left called "Bot" and click on "Add Bot".

On the bot page, you can give the bot a name like "TrebekBot" or some bot sounding username. This is the name that will appear in your server.

Lastly, you will want to add your bot to your server. To do this, click on the "OAuth2" tab of your Discord application. Under the "OAuth2 URL Generator", click the box that says "bot". Another menu should appear below that says "Bot Permissions". Under the "Bot Permissions", check the boxes for "Send Messages", "Manage Messages", "Read Message History", and "View Channels". Now copy the URL in the middle of the page and paste that in a new tab. You should now be able to pick which server you want to add the bot to (assuming you have the Manage Server permission on that server)

Once the bot has been installed on a server, make sure that server has a #jeopardy text channel, since this bot will only listen on the #jeopardy channel.

### Running the Code
In order to actually run the bot, you will need to have Python 3, virtualenv, and Redis installed on your computer. Ideally, you should also have some hosting solution (AWS, Azure, Google Cloud, etc) to run this bot full time so you do not have to leave it on your personal computer. For these instructions, it is assumed that you are running Unix.

First you must create your Python virtual environment so you can run the code. To do this, run the following commands in the project directory:

```
virtualenv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

Next you need to create a .env file with the authentication token for your app. To get the token, go back to your Discord application in the browser, click on the Bot tab, and copy the token there. Next create a file in the root of the project called .env (remember the period) and paste the following in that file:
```
DISCORD_TOKEN=<your bot token>
```
replacing \<your bot token\> with the token you copied from your browser.

You are now ready to run the bot. To run the bot in the background of your terminal, run the following from the project root:

```nohup ./venv/bin/python3 trebek.py > output.log 2>&1 &```

You should now be able to test the bot in your Discord server by typing "tb help" in the #jeopardy channel.

### Shutting down the Bot
If you ever need to shut down the bot to update the code, perform the following.

First, run the following command to get the process id of the bot

```ps -aux | grep "./venv/bin/python3 trebek.py"```

Note the process id next to the result (it should be the first number reading from the left, right after your username)

To actually stop the bot, run:

```kill -s TERM <PID>```

replacing \<PID\> with the process id you just found. Give the bot a few seconds to shut down, and then run the previous ```ps``` command again to verify that the process is gone.