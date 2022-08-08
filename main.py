import os
from dotenv import load_dotenv
import asyncio
import json

# discord packages
import discord
from discord.ext import commands

# import all Cogs
from cogs.backbone import Checker

# load the environment variable first
load_dotenv("./.env")

discord_token = os.getenv("DISCORD_TOKEN")

# must add intents to see guild members and activities
intents = discord.Intents.default()
intents.members = True
intents.presences = True

"""
user_id {
    game 1: VS Code,
    game 2: LOL,
    game 3: Multiversus
    game 4: Minecraft
}

method #1
whenever a task starts it will first 1.( try to get
their id from their name it will then 2.( try to see
if their name is in the json file
if it is then use the video game string data from there
to see if they are playing any games you want to announce (loop)
if it is NOT in the json file then go ahead and add its id
into the json file then ask for a video game to watch and
add that also into the json file then announce when they are
playing that game (loop)

method #2
!watch #member#

bot response: for which title?

admin response: Visual Studio Code

bot response: are there any other games?

(YES)
bot response: how many more games would you like to add?

admin response: 3

ar = admin response
bot response: please enter game 1 - ar - 2 - ar - 3

(PROMPT ADMIN AGAIN)

(CONTINUE)

1. try to get user id from name
2. try to see if the users id is in the json file (read)
Y. then add the video game string data to the file (write)
N. then add id to the file with the video game string (write)
3. read the file member ids and their games (read)
(LOOP START)
FOR EACH id check to see if they are online
    if id is online
        see what game id is playing (activity)
        if id is playing a game in list
            check to see if it is NOT recently_announce.name OR
            recently_announce.time > 10 OR
                annouce to discord

wait for 30s


"""

# intents = discord.Intents(members = True, presences = True)

# init bot
bot = commands.Bot(command_prefix="!watch ", intents=intents)


@bot.command(name="testing", help="testing out bot command")
async def testing_bot_command(ctx, users_name: str):
    # get specific discord user
    certain_user = discord.utils.get(ctx.guild.members, name=users_name)
    # check to see if user is online
    user_status = certain_user.status
    print(certain_user.status)
    response = f"{users_name} is appearing {user_status}"
    print(certain_user.id)
    # if they are online see what game they are playing
    # if no game is being played check again in 15s
    if user_status == discord.Status.online:
        game = certain_user.activity.name
        # if they are playing a game that is related to a string/object
        # then do something
        if game == "Visual Studio Code" or game == "Code":
            await ctx.send(f"{certain_user.name} is playing {game}")
    await ctx.send(response)


@bot.command(name="start", help="testing out bot command")
async def testing_bot_command2(ctx):
    bot.add_cog(Checker(bot, "./watching.json"))


@bot.command(name="stop")
async def stopping_test2(ctx):
    checker = bot.get_cog("Checker")
    checker.start_checking.stop()


@bot.command(name="add")
async def watch_new_user(ctx):

    # when the file does not exists
    if not os.path.exists("./watching.json"):
        watching_data_file = {"guild_id": ctx.guild.id, "members": []}
        with open("./watching.json", "w") as f:
            f.write(json.dumps(watching_data_file, indent=4))
    # when the file exists but the data is messed up
    if os.path.exists("./watching.json"):
        with open("./watching.json", "r") as f:
            data = json.load(f)
            if (data.get("guild_id") == None) or (data.get("members") == None):
                print("Please delete the current data file")
                await ctx.send("Data File is fucked")
                return

    await ctx.send("Who would you like to start watching?")

    f = open("./watching.json")
    data = json.load(f)
    f.close()

    def check(m):
        if m.author == ctx.author:
            return m

    def is_correct_member_response(m):
        if m.author.id == ctx.author.id and m.content:
            return m.content
    try:
        apparent_member_response_msg = await bot.wait_for("message", timeout=10.0, check=check)

    except asyncio.TimeoutError:
        await ctx.send("Could not find that member in your guild")
    else:
        await ctx.send(f"Is {apparent_member_response_msg.content} correct?")

        # confirm that this is the correct user
        try:
            confirm_response_msg = await bot.wait_for("message", timeout=10.0, check=is_correct_member_response)
        except asyncio.TimeoutError:
            print("Timed Out")
        else:
            if confirm_response_msg.content == "yes" or confirm_response_msg.content == "y":
                name = apparent_member_response_msg.content.split("#")[0]
                discrim = apparent_member_response_msg.content.split("#")[1]
                # this is where we find the user from the apparent_member_response_msg
                member = discord.utils.get(
                    ctx.guild.members, name=name, discriminator=discrim)

                # if guild member is already in the file
                for guild_member in data["members"]:
                    if member.id == guild_member["id"]:
                        print("User Already Being Watched")
                        await ctx.send("Guild member is already being watched\nPlease use the \"*!watch_update*\" command")
                        return
                print(f"{member.id} has been added")

                await ctx.send(f"How many games would you like to watch from {member.name}#{member.discriminator}?")
                try:
                    num_of_games_response_msg = await bot.wait_for("message", timeout=10.0, check=is_correct_member_response)
                except asyncio.TimeoutError:
                    print("Timed Out")
                else:
                    num_of_games = int(num_of_games_response_msg.content)
                    print(num_of_games)
                    game_titles = []
                    for i in range(1, num_of_games+1):
                        await ctx.send(f"Please enter title of game {i}")
                        try:
                            name_of_title_response_msg = await bot.wait_for("message", timeout=10.0, check=is_correct_member_response)
                        except asyncio.TimeoutError:
                            print("Timed Out: GAMES WERE NOT ADDED")
                            return
                        else:
                            game_title = name_of_title_response_msg.content.lower()
                            game_number = f"game {i}"
                            game_titles.append({game_number: game_title})

                    new_member_entry = {"id": member.id, "watching": {}}
                    for game in game_titles:
                        new_member_entry["watching"].update(game)
                    # members value is a list of members
                    data["members"].append(new_member_entry)
                    print(data)
                    with open("./watching.json", "w") as f:
                        f.write(json.dumps(data, indent=4))
            else:
                print("Sorry we couldn't find the right one?")


@bot.command(name="show")
async def show_watching_members(ctx):
    showing = ""
    with open("./watching.json", "r") as f:
        data = json.load(f)
        for member in data["members"]:
            try:
                member_obj = discord.utils.get(
                    ctx.guild.members, id=member["id"])
                if member_obj is not None:
                    member_watching_info = f"{member_obj.name}#{member_obj.discriminator}\nGAMES WATCHING\n"
                    games_watching = ""
                    for _, game in member["watching"].items():
                        games_watching = games_watching + game + "\n"
                    member_watching_info = member_watching_info + games_watching
                    showing = showing + "\n\n\n" + member_watching_info
                else:
                    print("No such memeber")
                    raise NameError("Not a member or Wrong Data")
            except NameError:
                showing = showing + "\n\n\n" + "*NOT A MEMBER*"
        await ctx.send(showing)


@bot.command(name="update")
async def update_watching_members(ctx, provided_name):
    int_to_emoji = {0: "0️⃣",
                    1: "1️⃣",
                    2: "2️⃣",
                    3: "3️⃣",
                    4: "4️⃣",
                    5: "5️⃣",
                    6: "6️⃣",
                    7: "7️⃣",
                    8: "8️⃣",
                    9: "9️⃣"}

    game_title_options = ["1️⃣", "2️⃣"]
    used_number_text = []

    # does the file exists
    if not os.path.exists("./watching.json"):
        ctx.send("No one is in the watch list")
        return

    # when the file exists but the data is messed up
    if os.path.exists("./watching.json"):
        with open("./watching.json", "r") as f:
            data = json.load(f)
            if (data.get("guild_id") == None) or (data.get("members") == None):
                print("Please delete the current data file")
                await ctx.send("Data File is fucked")
                return

    name = provided_name.split("#")[0]
    discrim = provided_name.split("#")[1]
    # find member
    member_obj = discord.utils.get(
        ctx.guild.members, name=name, discriminator=discrim)

    def check(m):
        if m.author.id == ctx.author.id:
            return m

    def reaction_check(reaction, user):
        return user == ctx.author and (str(reaction.emoji) in used_number_text or str(reaction.emoji) == "🟩")

    if member_obj != None:
        f = open("./watching.json")
        data = json.load(f)

        for member in data["members"]:
            if member["id"] == member_obj.id:
                games_text = "What game activity would you like to update?\n\n"
                # dict of what you are currently watching
                games = {}
                # takes any new/updated game titles
                new_games_watching = {}

                # get games then display them
                for key, game_title in member["watching"].items():
                    key_number = int(key.split(" ")[1])
                    number_text = int_to_emoji[key_number]
                    used_number_text.append(number_text)
                    games_text = games_text + f"{number_text} - {game_title}\n"
                    games.update({number_text: game_title})
                games_text = games_text + f"🟩 - Add new Game Title\n"
                # games.update({"🟩": "Add new Game Title"})
                message = await ctx.send(games_text)
                for num in used_number_text:
                    await message.add_reaction(num)
                
                # always add "🟩 - Add game"
                await message.add_reaction("🟩")

                # get reaction response
                try:
                    reaction, _ = await bot.wait_for("reaction_add", timeout=10.0, check=reaction_check)
                except asyncio.TimeoutError:
                    print("Timeout Error: No button chosen")
                    await ctx.send("You took to long")
                    return
                else:
                    counter = 1
                    for emoji, game_title in games.items():
                        if reaction.emoji == emoji:
                            # what would they like to do with game title
                            message = await ctx.send(f"What would you like to do to {game_title}?\n\n{game_title_options[0]} - Update\n{game_title_options[1]} - Delete")
                            for num in game_title_options:
                                await message.add_reaction(num)
                            try:
                                reaction, _ = await bot.wait_for("reaction_add", timeout=10.0, check=reaction_check)
                            except asyncio.TimeoutError:
                                print("Timeout")
                                await ctx.send("You took to long")

                                return
                            else:
                                # if update
                                if reaction.emoji == game_title_options[0]:
                                    await ctx.send("What is the name of the new game title?")
                                    try:
                                        game_title_response_msg = await bot.wait_for("message", timeout=10.0, check=check)
                                    except asyncio.TimeoutError:
                                        await ctx.send("Timed Out: Name was not entered")
                                        print(
                                            "Timed Out: Name was not entered")
                                        return
                                    else:
                                        print("hit")
                                        game_num = f"game {counter}"
                                        new_games_watching.update(
                                            {game_num: game_title_response_msg.content})
                                elif reaction.emoji == game_title_options[1]:
                                    counter = counter - 1
                                    await ctx.send(f"You have deleted {game_title}")
                        else:
                            game_num = f"game {counter}"
                            new_games_watching.update(
                                {game_num: game_title})
                        counter = counter + 1
                    if reaction.emoji == "🟩":
                        await ctx.send("What is the name of the new game title?")
                        try:
                            new_game_title_response_msg = await bot.wait_for("message", timeout=10.0, check=check)
                        except asyncio.TimeoutError:
                            print("Timed Out: No new game titled was added")
                            await ctx.send("Timed Out: No new game titled was added")
                            return
                        else:
                            new_num = f"game {counter}"
                            new_games_watching.update({new_num: new_game_title_response_msg.content})
                            await ctx.send(f"\"{new_game_title_response_msg.content}\" has been added")
                    
                    # set new games (if any) to member
                    if member["watching"].values() != new_games_watching.values():
                        print("new values added")
                        member["watching"] = new_games_watching
                        print(new_games_watching)
                        print(member)
                        with open("./watching.json", "w") as f:
                            f.write(json.dumps(data, indent=4))
                        return

                    # await ctx.send(reaction)

        await ctx.send(f"{name}#{discrim} is not being watched")
        return
    else:
        await ctx.send("This person is not a member")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("This is not a command")


bot.run(discord_token)
