from os import path

from dotenv import dotenv_values
from discord.ext import commands
from discord import app_commands
import discord

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def setup_hook(self):
        await self.tree.sync()
        print("Synced commands.")

    async def on_ready(self):
        print("Logged in as {self.user}")

if __name__ == "__main__":
    if not path.exists(".env"):
        raise FileNotFoundError(".env file dose not exsist!")

    secrets = dotenv_values(".env")

    if "DISCORD_TOKEN" not in secrets:
        raise ValueError(".env must include a DISCORD_TOKEN!")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = Bot(command_prefix="!", intents=intents)
    
    @bot.tree.command(name="ping", description="A test ping that reply 'pong' back to you")
    async def pingCommand(interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🤖")

    bot.run(secrets["DISCORD_TOKEN"])