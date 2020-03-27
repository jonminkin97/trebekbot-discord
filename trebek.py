import os
import discord
import random
import requests
import redis
import re
import json
from fuzzywuzzy import fuzz
from redis.exceptions import ConnectionError
from dotenv import load_dotenv

from discord.ext import commands

from trebekhelpcommand import TrebekHelpCommand

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# connect to the local Redis server
r = redis.Redis(host='localhost', db=0)
try:
    r.set('foo', 1)
    r.delete('foo')
except ConnectionError:
    print("Could not connect to Redis. Exiting")
    exit(1)

# TODO
# help pages

# define the bot itself
bot = commands.Bot(command_prefix='tb ', help_command=TrebekHelpCommand())

# confirmation message in the shell when connected to Discord
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Command to ask a new question
@bot.command(name='jeopardy', aliases=['j'], help="[j] Starts a new round of Discord Jeopardy, with a random category and price.")
async def get_question(ctx: commands.Context):
    # only play in the jeopardy channel
    if ctx.channel.name != "jeopardy":
        return

    # the shush key exists for 5 sec after a question has been asked
    if r.exists("shush"):
        return

    response = ""
    # Get the previous answer if it exists
    prev_question = r.get("question")
    if prev_question is not None:
        prev_question = json.loads(prev_question.decode())
        answer = prev_question.get("answer", "")
        response += "The answer is `{}`.\n".format(answer)

    # fetch a question from the api
    resp = requests.get('http://jservice.io/api/random')
    if not resp.ok:
        print("Failed to get question")
        await ctx.send("Failed to fetch question from Jeopardy API")
        return

    # pull the question fields out of the response
    question = resp.json()[0]
    category = question.get("category", {}).get("title", "")
    value= question.get("value", 0)
    if not value:
        value = 0
        question["value"] = 0
    question_text = question.get("question", "")

    # if the question has "seen here" in it, just get a new question
    while "seen here" in question:
        resp = requests.get('http://jservice.io/api/random')
        if not resp.ok:
            print("Failed to get question")
            await ctx.send("Failed to fetch question from Jeopardy API")
            return
        question = resp.json()[0]
        category = question.get("category", {}).get("title", "")
        value= question.get("value", 0)
        question_text = question.get("question", "")

    response += f'The category is `{category}` for ${value}: `{question_text}`'

    # put the question data in redis, turn on "shush", and set the answerable time
    r.set("question", json.dumps(question))
    r.setex("shush", 10, 1)
    r.setex("answerable", 35, 1)

    await ctx.send(response)
    

# Command to give an answer
@bot.command(name='answer', aliases=['a'], help="[a] Respond to the active round with your answer.")
async def parse_answer(ctx: commands.Context, *args):
    # only play in the jeopardy channel
    if ctx.channel.name != "jeopardy":
        return

    user = ctx.author.name
    # piece together the response from what the user typed
    user_response = ""
    for arg in args:
        user_response += f'{arg} '


    # check if user answered within 30 sec
    answerable = r.exists("answerable")

    question = r.get("question")

    # if there is no question to get, someone was probably a second late, so do nothing
    if not question:
        return

    # convert redis back to dictionary
    question = json.loads(question.decode())
    answer = question.get("answer", "")
    value = question.get("value", 0)
    question_id = question.get("id", 0)

    # check if the user responded with a question
    is_question_format = re.search("^(what|whats|where|wheres|who|whos)",
        re.sub("[^A-Za-z0-9_ \t]", "" , user_response), flags=re.I)

    # format the user's user_response to get their answer
    # replace & with and
    user_response = re.sub("\s+(&)\s+", " and ", user_response)
    # remove all punctuation
    user_response = re.sub("[^A-Za-z0-9_ \t]", "", user_response)
    # remove all question elements
    user_response = re.sub("^(what |whats |where |wheres |who |whos )", "", user_response, flags=re.I)
    user_response = user_response.strip()
    user_response = re.sub("^(is |are |was |were )", "", user_response, flags=re.I)
    user_response = user_response.strip()
    user_response = re.sub("^(the |a |an )", "", user_response, flags=re.I)
    user_response = user_response.strip()
    user_response = re.sub("\?+$", "", user_response)
    user_response = user_response.strip()
    user_response = user_response.lower()

    # format the correct answer
    answer = re.sub("[^A-Za-z0-9_ \t]", "", answer)
    answer = answer.strip()
    answer = re.sub("^(the|a|an)", "", answer, flags=re.I)
    answer = answer.strip()
    answer = answer.lower()

    # Do a fuzzy comparison to see if the user's answer is close enough to correct
    is_correct = (fuzz.ratio(user_response, answer) > 50)
    
    # print(f'Fuzz ratio between {user_response} and {answer}: {fuzz.ratio(user_response, answer)}')

    user_score = 0 if not r.get("score:" + user) else int(r.get("score:" + user).decode())

    # If the user has already attempted this question, shoo them away
    if r.exists(user + ":" + str(question_id)):
        await ctx.send(f'You had your chance, {user}. Let someone else answer.')
        return

    # if the user was wrong, deduct points, and shush them for the rest of this question
    if not is_correct:
        user_score -= value
        r.set("score:" + user, user_score)
        r.setex(user + ":" + str(question_id), 30, "true")
        await ctx.send(f'That is incorrect, {user}. Your score is now {"-$" + str(user_score * -1) if user_score < 0 else "$" + str(user_score)}')
        return

    # If the user did not respond within 30 sec, respond accordingly
    if not answerable:
        # clean up the keys in redis
        r.delete("question")
        r.delete("shush")
        r.delete("answerable")
        if is_correct:
            await ctx.send(f'That is correct, {user}, but time\'s up! Remember you only have 30 seconds to answer.')
        else:
            await ctx.send(f'Time\'s up, {user}. Remember, you have 30 seconds to answer.')
        return

    # If the user did not respond in the form of a question, deduct points and shush them for the rest of the qusestion
    if not is_question_format:
        user_score -= value
        r.set("score:" + user, user_score)
        r.setex(user + ":" + str(question_id), 30, "true")
        await ctx.send(f'That is correct, {user}, but responses have to be in the form of a question. Your score is now {"-$" + str(user_score * -1) if user_score < 0 else "$" + str(user_score)}.')
        return

    # The user answered correctly, so add points and delete the question
    user_score += value
    r.set("score:" + user, user_score)
    r.delete("question")
    r.delete("shush")
    r.delete("answerable")

    await ctx.send(f'That is correct, {user}. Your score is now {"-$" + str(user_score * -1) if user_score < 0 else "$" + str(user_score)}.')

# Command to show the leaderboard
@bot.command(name='leaderboard', aliases=['l'], help="[l] Shows the top scores.")
async def show_leaderboard(ctx: commands.Context):
    # only play in the jeopardy channel
    if ctx.channel.name != "jeopardy":
        return

    # fetch all the score keys from redis
    players = r.keys(pattern="score:*")
    scores = {}

    # for each key, convert it back to a string, get the value, and then put it in the score map
    for key in players:
        key = key.decode()
        score = int(r.get(key))
        scores[key[6:]] = score

    # sort the score map into an array of tuples (name, score)
    sorted_board = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    response = "Let's take a look at the top scores:\n"
    for i in range(0, len(sorted_board)):
        player = sorted_board[i]
        cash = "$" + str(player[1]) if player[1] >= 0 else "-$" + str(player[1] * -1)
        response += f'{i + 1}. {player[0]}: {cash}\n'

    await ctx.send(response)

@bot.command(name='score', aliases=['s'], help='[s] Shows your score.')
async def show_my_score(ctx: commands.Context):
    # only play in the jeopardy channel
    if ctx.channel.name != "jeopardy":
        return

    user = ctx.author.name

    score = r.get("score:" + user)

    if score is None:
        await ctx.send(f'{user}\'s score is $0')
        return

    score = int(score.decode())
    if score < 0:
        await ctx.send(f'{user}\'s score is -${score * -1}')
        return

    await ctx.send(f'{user}\'s score is ${score}')
    

    
# Command to give some Discord jeopardy wisdom
@bot.command(name='trebek', aliases=['t'], help='[t] Shows some Jeopardy wisdom')
async def get_quote(ctx: commands.Context):
    if ctx.channel.name != "jeopardy":
        return

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
