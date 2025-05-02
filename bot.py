from typing import Literal, TextIO, Optional, Any, cast, overload
from os import path
import traceback
import json

from dotenv import dotenv_values
from discord.ext import commands
from discord import app_commands
import discord

JSON_save = {"sort_keys": True, "indent": 4, "separators": (", ", ": ")}

ERROR_HEADER = (
    "\n-# (Please post the following stack trace to"
    + " (here)[github.com/Errorbot1122/pfp-alerter/issues])"
)
STACK_TRACE = "\n```\n{0}```"
ERROR_MESSAGE = ERROR_HEADER + STACK_TRACE


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        await self.tree.sync()
        print("Synced commands.")

    async def on_ready(self):
        print("Logged in as {self.user}")


def split_length(text: str, max_length: int) -> list[str]:
    """Split the text by text length

    Parameters
    ----------
    text : str
        the text you want to split
    max_length : int
        the maximum number of characters before a split (exclusive)

    Returns
    -------
    list[str]
        the list of splitted text
    """
    true_max_length = max_length - 1
    splits = [""]

    if len(text) < true_max_length:
        return [text]

    lines = text.splitlines()
    current_len = 0
    for line in lines:
        # Single Line that are too long get forcibly split
        # TODO: Add word level spiting
        while len(line) > true_max_length:
            splits[-1] = line[:true_max_length]
            line = line[true_max_length:]

            current_len = 0
            splits.append("")

        current_len += len(line)
        if current_len > true_max_length:
            current_len = len(line)
            splits.append(line)
        else:
            splits[-1] += "\n" + line

    return splits


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
        when you try to add a non-integer key to a list or `x` is not a
        list or dict.
    """

    if isinstance(x, list):
        if not isinstance(key, int):
            raise TypeError(
                f"Key of type {type(key)} is not allowed on list object!"
                + f"(Key: {str(key)})"
            )

        x.index(value, key)
    elif isinstance(x, dict):
        x[key] = value
    else:
        raise TypeError(f"Cannot create key on type '{type(x)}'! (Key: {str(key)})")


@overload
def get_save_from_guild(
    guild: discord.Guild, file_descriptor: Literal[False] = False
) -> tuple[Any, None]: ...
@overload
def get_save_from_guild(
    guild: discord.Guild, file_descriptor: Literal[True]
) -> tuple[Any, TextIO]: ...
def get_save_from_guild(
    guild: discord.Guild, file_descriptor: bool = False
) -> tuple[Any, Optional[TextIO]]:
    """Gets all the save for the chosen guild.

    Parameters
    ----------
    guild : discord.Guild
        the chosen guild (server) to get the save for.
    file_descriptor : bool, optional
        choses wether to return the opened file or not, by default
        `False`

    Returns
    -------
    tuple[dict, Optional[TextIOWrapper]]
        returns the save data with the file. (file only if
        `file_descriptor` is True)

    Raises
    ------
    FileNotFound
        when `save/[guild_id].json` dose not already exist
    """

    file_path = "save/" + str(guild.id) + ".json"
    if not path.exists(file_path):
        open(file_path, "w").close()

    file = open(file_path, "r+" if file_descriptor else "r")
    try:
        data = json.load(file)
    except json.JSONDecodeError as e:
        data = {}

    if file_descriptor:
        file.seek(0)
        return (data, file)
    else:
        file.close()
        return (data, None)


def save_guild_data(
    guild: discord.Guild,
    data: Any,
    key: Optional[Any | list[Any]] = None,
    create_keys: bool = False,
):
    """Save ether a single setting or overwrite all the settings for a
    guild.

    Parameters
    ----------
    guild : discord.Guild
        the chosen guild (server) to get the save for
    data : Any
        the data that you want to overwrite
    key : Optional[any, list[any]], optional
        The specific setting you want to overwrite, if `None`, overwrite
         every setting

        If the setting is nested, separate each key in a list or in a
        period separated string. By default `None`
    create_keys : bool, optional
        Wether the create new keys if not existing already, by default
        `False`

    Raises
    ------
    FileNotFoundError
        when `key` is has a value and `create_keys` is `False` **OR**
        the `settings` folder dose not exist.
    KeyError
        when one of your keys don't exist in the settings and
        `create_keys` is `False`  or if `create_keys` is `True` and you
        are trying to add an string key to a list.
    TypeError
        when you try to add a non-integer key to a list or you try to
        key an un-keyable value *(not list or dict)*.
    """

    if isinstance(key, str):
        key = key.split(".")

    try:
        current_data, file = get_save_from_guild(guild, True)
    except FileNotFoundError as e:
        # Can't do anything about that, so relay that to the devs...
        if key is not None and not create_keys:
            raise e

        file = open("save/" + str(guild.id) + ".json", "w+")
        current_data = {}

    try:
        file: TextIO = file
        # No key = overwrite
        if key is None:
            json.dump(data, file, **JSON_save)
            return

        # Nest into the last entry before the data
        constrained_data = current_data
        for current_key in key[:-1]:

            if create_keys and current_key not in constrained_data:
                set_json_key(constrained_data, current_key, {})
            constrained_data = constrained_data[current_key]

        # Overwrite the key
        set_json_key(constrained_data, key[-1], data)
        json.dump(current_data, file, **JSON_save)
        file.truncate()
    finally:
        file.close()


@overload
def get_key(
    data: Any, key: Any | list[Any], allow_errors: Literal[False] = False
) -> Any | None: ...
@overload
def get_key(data: Any, key: Any | list[Any], allow_errors: Literal[True]) -> Any: ...
def get_key(data: Any, key: Any | list[Any], allow_errors: bool = False) -> Any | None:
    """Finds the corresponding value with a key in json data.

    Parameters
    ----------
    data : Any
        the json data you want to search
    key : Any | list[Any]
        the specific location you want to get the key from, if the value
        is nested, separate each key in a list or in a period separated
        string.
    allow_errors : bool, optional
        weather to allow raising KeyError instead of return None, by
        default False

    Returns
    -------
    Any | None
        The value wanted if found

    Raises
    ------
    KeyError
        If a key could not be found
    """
    if isinstance(key, str):
        key = key.split(".")

    constrained_data = data
    for key_index in range(len(key)):
        current_key = key[key_index]
        if current_key not in constrained_data:
            if allow_errors:
                raise KeyError(f"Cannot find key at {".".join(key[:key_index])}!")
            else:
                return None

        try:
            constrained_data = constrained_data[current_key]
        except TypeError as e:
            if allow_errors:
                raise TypeError(
                    f"Cannot get key on type '{type(constrained_data)}' "
                    + f"({".".join(key[:key_index])})"
                )
            else:
                return None

    return constrained_data


if __name__ == "__main__":
    if not path.exists(".env"):
        raise FileNotFoundError(".env file dose not exist!")

    secrets = dotenv_values(".env")

    if "DISCORD_TOKEN" not in secrets:
        raise ValueError(".env must include a DISCORD_TOKEN!")

    intents = discord.Intents(
        guilds=True, members=True, guild_messages=True, message_content=True
    )
    bot = Bot(command_prefix="!", intents=intents)

    @bot.check
    def check_guild():
        async def predicate(interaction: discord.Interaction):
            if interaction.guild is None:
                raise app_commands.CheckFailure(
                    "This command can only be run in a server."
                )

            return True

        return app_commands.check(predicate)

    def check_perms():
        async def predicate(interaction: discord.Interaction):
            if interaction.guild is None:
                return False

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
        name="optout",
        description="Chose to opt out of alerting users when you change your profile "
        + "picture or display name change.",
    )
    async def optOut(interaction: discord.Interaction):
        opt_out_key = ["members", str(interaction.user.id), "opt_out"]
        guild = cast(discord.Guild, interaction.guild)

        save, _ = get_save_from_guild(guild)
        already_opted_out: bool = get_key(save, opt_out_key) or False

        if already_opted_out:
            await interaction.response.send_message(
                "You are already opted out! Run `/optin` to opt back in.",
                ephemeral=True,
            )
            return

        save_guild_data(guild, True, opt_out_key, create_keys=True)

        await interaction.response.send_message(
            "✔ You have successfully been opted out! Run `/optin` to opt back in.",
            ephemeral=True,
        )

    @bot.tree.command(
        name="optin",
        description="Chose to opt into alerting users when you change your profile "
        + "picture or display name change.",
    )
    async def optIn(interaction: discord.Interaction):
        opt_out_key = ["members", str(interaction.user.id), "opt_out"]
        guild = cast(discord.Guild, interaction.guild)

        save, _ = get_save_from_guild(guild)
        already_opted_out: bool = get_key(save, opt_out_key) or False

        if not already_opted_out:
            await interaction.response.send_message(
                "You are already opted in! Run `/optout` to opt out.", ephemeral=True
            )
            return

        save_guild_data(guild, False, opt_out_key, create_keys=True)

        await interaction.response.send_message(
            "✔ You have successfully been opted in! Run `/optout` to opt back in.",
            ephemeral=True,
        )

    @bot.tree.command(
        name="setchannel", description="Sets the channel for sending alerts."
    )
    @check_perms()
    async def setChannelCommand(
        interaction: discord.Interaction, channel: discord.TextChannel
    ):
        if interaction.guild is None or channel.guild.id != interaction.guild.id:
            await interaction.response.send_message(
                "Channel not in current server! Please enter a guild in this server."
            )
            return

        try:
            save_guild_data(
                channel.guild, channel.id, key="setting.channel", create_keys=True
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
    @check_perms()
    async def testAlert(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "You are currently not in a sever!", ephemeral=True
            )
            return

        try:
            save, _ = get_save_from_guild(interaction.guild)
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.response.send_message(
                "Could not save file because an error has occurred!"
                + ERROR_MESSAGE.format(str(tb))
            )
            return

        channel_id = get_key(save, "setting.channel")
        if not channel_id:
            await interaction.response.send_message(
                "Channel save not set! Please run `/setchannel` to fix.",
                ephemeral=True,
            )
            return

        channel = cast(discord.TextChannel, bot.get_channel(channel_id))
        if channel is None:
            await interaction.response.send_message(
                "Channel dose not exist! Please set a new one by running "
                + "`/setchannel`.",
                ephemeral=True,
            )
            return

        alert = await channel.send("🚨 This is a test alert, 123 🚨")

        await interaction.response.send_message(
            f"Test completed successfully!\n-# Jump to msg: {alert.jump_url}",
            ephemeral=True,
        )

        await alert.delete(delay=5)

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
                "An unknown error has occurred! " + ERROR_HEADER, ephemeral=True
            )

            print(str(tb))
            # Fix for 2000 char max message
            # TODO: Send to log files and send log id instead
            split_traceback = split_length(str(tb), 1993)  # -7 characters for codeblock
            for trace_part in split_traceback:
                await interaction.followup.send("```" + trace_part + "\n```")

    bot.run(cast(str, secrets["DISCORD_TOKEN"]))
