from discord.ext import tasks, commands
import discord
import os
import os.path
import json
from datetime import datetime
class Checker(commands.Cog):
    def __init__(self, bot, filepath):
        self.bot = bot
        # load json file on start
        self.filepath = filepath
        f = open(self.filepath)
        data = json.load(f)
        f.close()

        self.guild_id = data["guild_id"]
        self.watching_members = data["members"]

        self.start_checking.start()

    async def getMember(self, guild_id, member_id):
        guild = self.bot.get_guild(guild_id)
        member = discord.utils.get(guild.members, id=member_id)

        return member 
     
    @tasks.loop(seconds=5.0)
    async def start_checking(self):
        print("you are checking\n")

        for member in self.watching_members:
            member_obj = await self.getMember(self.guild_id, member["id"])
            if member_obj.status == discord.Status.online:
                games_watching = member["watching"].values()
                current_activity = member_obj.activity.name.lower()
                if current_activity in games_watching:
                    # get the timestamp for this moment
                    now = datetime.timestamp(datetime.now())
                    if ("last_checked" not in member) or (member["last_checked"]["name"] != current_activity) or (now - member["last_checked"]["timestamp"] > 30):
                        print(f"{member_obj.id} is playing {member_obj.activity.name}")
                        # update last_checked
                        last_checked = {"name": current_activity, "timestamp": now}
                        member["last_checked"] = last_checked
                        print(member)
                    else:
                        print("waiting 30s")

            


    @start_checking.before_loop
    async def before_checking(self):
        print("Starting Checker Loop")
        await self.bot.wait_until_ready()
        



    
    @start_checking.after_loop
    async def on_checker_cancel(self):
        print("Stopping Checker Loop")
        watching_json = {"guild_id": self.guild_id, "members": self.watching_members}
        # save current watching data
        with open(self.filepath, "w") as f:
            f.write(json.dumps(watching_json, indent=4))
