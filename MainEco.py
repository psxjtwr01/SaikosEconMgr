import asyncio
import json
import os
from datetime import datetime, timedelta
import revolt
from revolt.ext import commands
from aiohttp import ClientSession
import econmgr
import colorama,time
def debug(text, errlevl=0):
    if errlevl == 0:
        text = colorama.Fore.YELLOW + "[!] " + colorama.Fore.RESET + text
    else:
        text = colorama.Fore.GREEN + "[sys] " + colorama.Fore.RESET + text

# Revolt Bot Class
class RevoltBot(commands.CommandsClient):
    def __init__(self, command_prefix, **kwargs):
        super().__init__(**kwargs)
        self.command_prefix = command_prefix
        self.data = econmgr.load_data()
        self.last_used = {}
        self.commands_dict = {
            "help": self.cog_command,
            "hello": self.hello_command,
            "gamble": self.gamble_command,
            "bal": self.bal_command,
            "work": self.work_command,
            "rob": self.rob_command,
            "giveahomiehead": self.give_ahomie_head_command,
            "cd": self.cd_command,
            
        }

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message):
        username = message.author.name
        if message.author.bot:
            return
        if not message.content.startswith(self.command_prefix):
            channel_name = message.channel.name
            debug(f"{username} said '{message.content}' in channel '{channel_name}'")
            return
        command, *args = message.content[len(self.command_prefix):].split()
        command = command.lower()
        
        if command and command in self.commands_dict:
            debug(f"{username} ran command '{command}' with args '{args}' ")
            await self.commands_dict[command](message, *args)
    

    async def cog_command(self, message, *args):
        embed = revolt.SendableEmbed(
            title="** S A I K O - ❤ **",
            description="",
            colour="#448ccc"
        )

        embed.description = (
            "** Created by drexxy **\n\n"
           
            "### Help:\n"
            "  Displays this help message\n\n"
            "### Hello:\n"
            "  Saiko greets you in a friendly manner\n\n"
            "### Gamble amount:\n"
            "  You gamble a certain positive amount of money. You have a 30% chance of winning.\n\n"
            "### Work:\n"
            "  You can do a job every hour to gain an amount of money based on your level.\n\n"
            "### Bal:\n"
            "  Saiko sends your balance and level. You can also specify a user to check their balance.\n\n"
            "### Rob user:\n"
            "  You rob a user for a random amount of money.\n\n"
            "### GiveAhomieHead:\n"
            "  You can give a homie head (no money L).\n\n"
            "### CD:\n"
            "  You can check the cooldown of your work. You can also specify a user and check their cooldowns as well.\n\n"
            
            "=== prefix is `?` for all commands ==="
        )

        #embed.set_thumbnail(url="https://imgur.com/a/MER5CI7")  # Optional: Add a thumbnail image
        #embed.media = "https://i.imgur.com/pgRiOsM.png"
        

        await message.reply(embed=embed)

    async def hello_command(self, message, *args):
        await message.reply(f"Hello, {message.author.mention}! How are you today?")
    
    async def gamble_command(self, message, amount: str):
        if self.is_on_cooldown(message.author.id, "gamble"):
            await message.reply("This command is on cooldown. Please wait a bit.")
            return

        response = econmgr.gamble(message.author.id, amount)
        await message.reply(response)
        self.set_cooldown(message.author.id, "gamble")

    async def bal_command(self, message, *args):
        if self.is_on_cooldown(message.author.id, "bal"):
            await message.reply("This command is on cooldown. Please wait a bit.")
            return

        member = message.mentions[0] if message.mentions else message.author
        response = econmgr.get_balance(member.id)
        await message.reply(response)
        self.set_cooldown(message.author.id, "bal")

    async def work_command(self, message, *args):
        if self.is_on_cooldown(message.author.id, "work"):
            await message.reply("This command is on cooldown. Please wait a bit.")
            return

        response = econmgr.work(message.author.id)
        await message.reply(response)
        self.set_cooldown(message.author.id, "work")

    async def rob_command(self, message, *args):
        if self.is_on_cooldown(message.author.id, "rob"):
            await message.reply("This command is on cooldown. Please wait a bit.")
            return

        if not message.mentions:
            await message.reply("Please mention a user to rob.")
            return

        member = message.mentions[0]
        response = econmgr.rob(message.author.id, member.id)
        await message.reply(response)
        self.set_cooldown(message.author.id, "rob")

    async def give_ahomie_head_command(self, message, *args):
        await message.reply(f"{message.author.mention} gave a homie head (no money involved)")

    async def cd_command(self, message, command: str = None, *args):
        if self.is_on_cooldown(message.author.id, "cd"):
            await message.reply("This command is on cooldown. Please wait a bit.")
            return

        if command:
            if command not in econmgr.cooldowns:
                await message.reply("Unknown command.")
                return

            member = message.mentions[0] if message.mentions else message.author
            cooldown_end = self.last_used.get(str(member.id), {}).get(command)
            if cooldown_end:
                remaining = (cooldown_end + econmgr.cooldowns[command]) - datetime.now()
                if remaining > timedelta(0):
                    await message.reply(f"{member.mention}'s cooldown for {command} is {remaining} remaining.")
                else:
                    await message.reply(f"{member.mention} has no cooldown for {command}.")
            else:
                await message.reply(f"{member.mention} has not used {command} yet.")
        else:
            await message.reply("Please specify a command to check cooldown.")

        self.set_cooldown(message.author.id, "cd")

    def is_on_cooldown(self, user_id, command):
        now = datetime.now()
        if user_id in self.last_used and command in self.last_used[user_id]:
            return now - self.last_used[user_id][command] < econmgr.cooldowns[command]
        return False

    def set_cooldown(self, user_id, command):
        now = datetime.now()
        if user_id not in self.last_used:
            self.last_used[user_id] = {}
        self.last_used[user_id][command] = now

# Main function to run the bot
async def main():
    async with ClientSession() as session:
        bot = RevoltBot(
            command_prefix="?",
            session=session,
            token="yQGrlfbAclnzjLjGXuiMfiv5xsrSlJ2uXTsju52uYY5HUWQY4YALbXk-ieadh3oL",
            api_url="https://api.revolt.chat",
            bot=True
        )
        await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
