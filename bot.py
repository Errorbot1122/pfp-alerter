from os import path

from dotenv import dotenv_values
import discord

class Client(discord.Client):
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

    client = Client(intents=intents)
    client.run(secrets["DISCORD_TOKEN"])