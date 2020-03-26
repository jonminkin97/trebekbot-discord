import os
import discord
import random
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client = discord.Client()

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     response = "It is I the great and powerful trebek"

#     if message.content == "tb":
#         await message.channel.send(response)

# client.run(TOKEN)

bot = commands.Bot(command_prefix='tb ')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# @bot.command(name='hi')
# async def trebek(ctx):
#     response = "It is I the great and powerful bot"

#     await ctx.send(response)

# bot.run(TOKEN)


@bot.command(name='trebek')
async def on_message(ctx):
    quotes = ["Welcome back to Discord Jeopardy. Before we begin this Jeopardy round, I'd like to ask our contestants once again to please refrain from using ethnic slurs.",
              "Okay, Turd Ferguson.",
              "I hate my job.",
              "Let's just get this over with.",
              "Do you have an answer?",
              "I don't believe this. Where did you get that magic marker? We frisked you on the way in here.",
              "What a ride it has been, but boy, oh boy, these Discord users did not know the right answers to any of the questions.",
              "Back off. I don't have to take that from you.",
              "That is _awful_.",
              "Okay, for the sake of tradition, let's take a look at the answers.",
              "Beautiful. Just beautiful.",
              "And welcome back to Discord Jeopardy. Because of what just happened before during the commercial, I'd like to apologize to all blind people and children.",
              "Thank you, thank you. Moving on.",
              "I really thought that was going to work.",
              "Wonderful. Let's take a look at the categories. They are: `Potent Potables`, `Point to your own head`, `Letters or Numbers`, `Will this hurt if you put it in your mouth`, `An album cover`, `Make any noise`, and finally, `Famous Muppet Frogs`. I should add that the answer to every question in that category is `Kermit`.",
              "For the last time, that is not a category.",
              "Unbelievable.",
              "Great. Let's take a look at the final board. And the categories are: `Potent Potables`, `Sharp Things`, `Movies That Start with the Word Jaws`, `A Petit Déjeuner` -- that category is about French phrases, so let's just skip it.",
              "Enough. Let's just get this over with. Here are the categories, they are: `Potent Potables`, `Countries Between Mexico and Canada`, `Members of Simon and Garfunkel`, `I Have a Chardonnay` -- you choose this category, you automatically get the points and I get to have a glass of wine -- `Things You Do With a Pencil Sharpener`, `Tie Your Shoe`, and finally, `Toast`.",
              "Better luck to all of you, in the next round. It's time for Discord Jeopardy, let's take a look at the board. And the categories are: `Potent Potables`, `Literature` -- which is just a big word for books -- `Therapists`, `Current U.S. Presidents`, `Show and Tell`, `Household Objects`, and finally, `One-Letter Words`.",
              "Uh, I see. Get back to your podium.",
              "You look pretty sure of yourself. Think you've got the right answer?",
              "Welcome back to Discord Jeopardy. We've got a real barnburner on our hands here.",
              "And welcome back to Discord Jeopardy. I'd like to once again remind our contestants that there are proper bathroom facilities located in the studio.",
              "Welcome back to Discord Jeopardy. Once again, I'm going to recommend that our viewers watch something else.",
              "Great. Better luck to all of you in the next round. It's time for Discord Jeopardy. Let's take a look at the board. And the categories are: `Potent Potables`, `The Vowels`, `Presidents Who Are On the One Dollar Bill`, `Famous Titles`, `Ponies`, `The Number 10`, and finally: `Foods That End In \"Amburger\"`.",
              "Let's take a look at the board. The categories are: `Potent Potables`, `The Pen is Mightier` -- that category is all about quotes from famous authors, so you'll all probably be more comfortable with our next category -- `Shiny Objects`, continuing with `Opposites`, `Things you Shouldn't Put in Your Mouth`, `What Time is It?`, and, finally, `Months That Start With Feb`."
            ]
    response = random.choice(quotes)
    await ctx.send(response)


bot.run(TOKEN)
