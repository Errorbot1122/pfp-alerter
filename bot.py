from typing import Literal, TextIO, Optional, Any, cast, overload
from os import path
from time import sleep
import traceback
import json

from aiohttp import client
from dotenv import dotenv_values
from discord.ext import commands
from discord import app_commands, channel, guild, message
import discord

JSON_SETTINGS = {"sort_keys": True, "indent": 4, "separators": (", ", ": ")}

ERROR_MESSAGE = (
    "\n-# (Please post the following stack trace to"
    + " [here](github.com/Errorbot1122/pfp-alerter/issues))\n```\n{0}```"
)

UNKNOWN_ERROR_MSG = "An unknown error has occurred! " + ERROR_MESSAGE


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        await self.tree.sync()
        print("Synced commands.")

    async def on_ready(self):
        print("Logged in as {self.user}")


def set_json_key(x: Any, key: Any, value: Optional[Any] = None):
    """Add/overwrites a key on json data.

    Parameters
    ----------
    x : Any
        the list or dict you want to add a key for
    key : Any
        the index/key of where you want to enter the value
    value : Optional[Any], optional
        the value you want to set it to, by default None

    Raises
    ------
    TypeError
        when you try to add a non-integer key to a list or `x` is not a list or dict.
    """

    if isinstance(x, list):
        if not isinstance(key, int):
            raise TypeError(
                f"Key of type {type(key)} is not allowed on list object! (Key: {str(key)})"
            )

        x.index(value, key)
    elif isinstance(x, dict):
        x[key] = value
    else:
        raise TypeError(f"Cannot access key on type '{type(x)}'! (Key: {str(key)})")


@overload
def get_settings_from_guild(
    guild: discord.Guild, file_descriptor: Literal[False] = False
) -> tuple[Any, None]: ...
@overload
def get_settings_from_guild(
    guild: discord.Guild, file_descriptor: Literal[True]
) -> tuple[Any, TextIO]: ...
def get_settings_from_guild(
    guild: discord.Guild, file_descriptor: bool = False
) -> tuple[Any, Optional[TextIO]]:
    """Gets all the settings for the chosen guild.

    Parameters
    ----------
    guild : discord.Guild
        the chosen guild (server) to get the settings for.
    file_descriptor : bool, optional
        choses wether to return the opened file or not, by default `False`

    Returns
    -------
    tuple[dict, Optional[TextIOWrapper]]
        returns the save data with the file. (file only if `file_descriptor` is True)

    Raises
    ------
    FileNotFound
        when `settings/[guild_id].json` dose not already exist
    """

    file = open("settings/" + str(guild.id) + ".json", "w+" if file_descriptor else "r")
    try:
        data = json.loads(file.read())
    except:
        data = {}

    if file_descriptor:
        return (data, file)
    else:
        file.close()
        return (data, None)


def save_guild_setting(
    guild: discord.Guild,
    data: dict | Any,
    key: Optional[Any | list[Any]] = None,
    create_keys: bool = False,
):
    """Save ether a single setting or overwrite all the settings for a guild.

    Parameters
    ----------
    guild : discord.Guild
        the chosen guild (server) to get the settings for
    date : dict | any
        the data that you want to overwrite
    key : Optional[any, list[any]], optional
        The specific setting you want to overwrite, if `None`, overwrite every setting

        If the setting is nested, separate each key in a list or in a period separated
        string. By default `None`
    create_keys : bool, optional
        Wether the create new keys if not existing already, by default `False`

    Raises
    ------
    FileNotFoundError
        when `key` is has a value and `create_keys` is `False` **OR** the `settings`
        folder dose not exist.
    KeyError
        when one of your keys don't exist in the settings and `create_keys` is `False`
        or if `create_keys` is `True` and you are trying to add an string key to a list.
    TypeError
        when you try to add a non-integer key to a list or you try to key an un-keyable
        value (not list or dict).
    """

    if isinstance(key, str):
        key = key.split(".")

    try:
        current_data, file = get_settings_from_guild(guild, True)
    except FileNotFoundError as e:
        # Can't do anything about that, so relay that to the devs...
        if key is not None and not create_keys:
            raise e

        file = open("settings/" + str(guild.id) + ".json", "w+")
        current_data = {}

    try:
        file: TextIO = file
        # No key = overwrite
        if key is None:
            json.dump(data, file, **JSON_SETTINGS)
            return

        # Nest into the last entry before the data
        constrained_data = current_data
        for key_index in range(len(key) - 1):
            current_key = key[key_index]
            if create_keys and current_key not in constrained_data:
                set_json_key(constrained_data, current_key, {})
            constrained_data = constrained_data[current_key]

        # Overwrite the key
        set_json_key(constrained_data, key[-1], data)
        json.dump(current_data, file, **JSON_SETTINGS)
    finally:
        file.close()


if __name__ == "__main__":
    if not path.exists(".env"):
        raise FileNotFoundError(".env file dose not exsist!")

    secrets = dotenv_values(".env")

    if "DISCORD_TOKEN" not in secrets:
        raise ValueError(".env must include a DISCORD_TOKEN!")

    intents = discord.Intents(
        guilds=True, members=True, guild_messages=True, message_content=True
    )
    bot = Bot(command_prefix="!", intents=intents)

    def check_perms():
        async def predicate(interaction: discord.Interaction):
            if interaction.guild is None:
                raise app_commands.CheckFailure(
                    "This command can only be run in a server."
                )

            bot_member = interaction.guild.me
            user_member = cast(discord.Member, interaction.user)

            if bot_member is None:
                raise app_commands.CheckFailure("Bot member not found.")

            return user_member.top_role <= bot_member.top_role

        return app_commands.check(predicate)

    @bot.tree.command(
        name="ping", description="A test ping that reply 'pong' back to you"
    )
    async def pingCommand(interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🤖")

    @bot.tree.command(
        name="setchannel", description="Sets the channel for sending alerts."
    )
    async def setChannelCommand(
        interaction: discord.Interaction, channel: discord.TextChannel
    ):
        if interaction.guild is None or channel.guild.id != interaction.guild.id:
            await interaction.response.send_message(
                "Channel not in current server! Please enter a guild in this server."
            )
            return

        try:
            save_guild_setting(
                channel.guild, channel.id, key="channel", create_keys=True
            )
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.response.send_message(ERROR_MESSAGE.format(str(tb)))
            return

        await interaction.response.send_message(
            f"Successfully set output channel to {channel.jump_url}.", ephemeral=True
        )

    @bot.tree.command(
        name="testalert", description="Tests sending an alert to the chosen channel"
    )
    async def testAlert(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "You are currently not in a sever!", ephemeral=True
            )
            return

        try:
            settings, _ = get_settings_from_guild(interaction.guild)
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.response.send_message(
                "Could not save file because an error has occurred!"
                + ERROR_MESSAGE.format(str(tb))
            )
            return

        if "channel" not in settings:
            await interaction.response.send_message(
                "Channel setting not set! Please run `/setchannel` to fix.",
                ephemeral=True,
            )
            return

        channel = cast(discord.TextChannel, bot.get_channel(settings["channel"]))
        if channel is None:
            await interaction.response.send_message(
                "Channel dose not exist! Please set a new one by running `/setchannel`.",
                ephemeral=True,
            )
            return

        await channel.send("🚨 This is a test alert, 123 🚨")

        await interaction.response.send_message(
            "Test completed successfully!", ephemeral=True
        )

    # Error handling
    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "🚫 You don't have the required permissions to run this command.",
                ephemeral=True,
            )

        elif isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                f"🚫 You need the `{error.missing_role}` role to run this command.",
                ephemeral=True,
            )

        elif isinstance(error, app_commands.TransformerError):
            await interaction.response.send_message(
                "❗ Invalid value provided. Please check your input and try again.",
                ephemeral=True,
            )

        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                # Default error message if non
                str(error) or "❌ You don't meet the requirements to use this command.",
                ephemeral=True,
            )
        else:
            tb = traceback.format_exc()
            await interaction.response.send_message(
                UNKNOWN_ERROR_MSG.format(str(tb)), ephemeral=True
            )

    bot.run(cast(str, secrets["DISCORD_TOKEN"]))
