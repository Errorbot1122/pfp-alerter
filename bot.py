from typing import (
    TextIO,
    Callable,
    Literal,
    Any,
    TypeVar,
    ParamSpec,
    Optional,
    Awaitable,
    cast,
    overload,
)
from contextlib import contextmanager
from collections.abc import Generator
from datetime import datetime
from random import choice
from io import BytesIO
from os import path

import traceback
import requests
import inspect
import json


from dotenv import dotenv_values
from discord.ext import commands, tasks
from discord import Embed, app_commands
from discord.app_commands import AppCommandError as AppCommandErrorBase
import discord


JSON_SAVE_PERMS = {"sort_keys": True, "indent": 4, "separators": (", ", ": ")}

ERROR_FOOTER = (
    "-# (Please post the following stack trace to"
    + " (here)[github.com/Errorbot1122/pfp-alerter/issues])"
)
STACK_TRACE = "\n```\n{0}```"
ERROR_MESSAGE = ERROR_FOOTER + STACK_TRACE

EMBED_DEFAULT_COLOR = discord.Color.purple()
EMBED_ERROR_COLOR = discord.Color.magenta()

FALLBACK_IMAGE = "./assets/not_found.png"

FUNNY_MESSAGES: dict[str, list[str]] = {
    "common": [
        "Bro really changed his {0} :sob:",
        "I fr got nothing to say :neutral_face:",
        "Did bro get hacked :skull::pray:",
        "\\*no comment\\* :no_mouth:",
    ],
    "name": [],
    "avatar": [],
    "both": [],
}

T = TypeVar("T")
P = ParamSpec("P")


class AppCommandError(AppCommandErrorBase):
    pass


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        await self.tree.sync()
        print("Synced commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user}")


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


@contextmanager
def add_exception_notes(notes: str | list[str]) -> Generator[None, None, None]:
    """Add a note to any exception raised within this context block.

    Parameters
    ----------
    notes : str | list[str]
        the note(s) to attach to any exception raised inside the context
        block.

        This note will be added using the `add_note` method if
        available.

    Yields
    ------
    None
        the context block executes normally unless an exception is
        raised.

    Raises
    ------
    Exception
        any exception raised inside the context block will be re-raised
        after the notes are attached.

    Examples
    --------
    >>> with exception_note("Error occurred while reading data!"):
    ...     with open("invalid.txt", "r") as f:
    ...         print("Read was successful")
    Traceback (most recent call last):
        ...
    FileNotFoundError: [Errno 2] No such file or directory: 'invalid.txt'
    Error occurred while reading data!
    """
    if isinstance(notes, str):
        notes = [notes]
    try:
        yield
    except Exception as e:
        try:
            for note in notes:
                e.add_note(note)
        except AttributeError:
            pass
        raise


def safe_call(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> tuple[T, None] | tuple[None, BaseException]:
    """Safely calls a function with the given arguments and handles
    exceptions. _(Synchronously)_

    Parameters
    ----------
    func : Callable
        the function to call
    *args : Any
        positional arguments to pass to the function
    **kwargs : Any
        keyword arguments to pass to the function

    Returns
    -------
    tuple[Any | None, Exception | None]
        returns a tuple containing the **result and `None`** if no
        Exception occurs and **`None` and `Exception`** if it dose.
    """
    try:
        result = func(*args, **kwargs)
        return (result, None)
    except Exception as e:
        return (None, e)


async def safe_call_async(
    func: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs
) -> tuple[T, None] | tuple[None, BaseException]:
    """Safely calls a function with the given arguments and handles
    exceptions. _(Asynchronously)_

    Parameters
    ----------
    func : Callable
        the function to call
    *args : Any
        positional arguments to pass to the function
    **kwargs : Any
        keyword arguments to pass to the function

    Returns
    -------
    tuple[Any | None, Exception | None]
        returns a tuple containing the **result and `None`** if no
        Exception occurs and **`None` and `Exception`** if it dose.
    """

    if not inspect.iscoroutinefunction(func):
        return cast(
            tuple[T, None] | tuple[None, BaseException],  # Cast to resolve type checker
            safe_call(func, *args, **kwargs),
        )

    try:
        return (await func(*args, **kwargs), None)
    except Exception as e:
        return (None, e)


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


def download_image(url: str) -> bytes:
    """Download an image from a URL and return it as a BytesIO object.

    Parameters
    ----------
    url : str
        the URL of the image to download.

    Returns
    -------
    io.BytesIO
        BytesIO object containing the image data.

    Raises
    ------
    requests.HTTPError
        when the image could not be downloaded (non-200 status code).
    """
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()

    return response.content


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
            json.dump(data, file, **JSON_SAVE_PERMS)
            return

        # Nest into the last entry before the data
        constrained_data = current_data
        for current_key in key[:-1]:

            if create_keys and current_key not in constrained_data:
                set_json_key(constrained_data, current_key, {})
            constrained_data = constrained_data[current_key]

        # Overwrite the key
        set_json_key(constrained_data, key[-1], data)
        json.dump(current_data, file, **JSON_SAVE_PERMS)
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
        if constrained_data is None or current_key not in constrained_data:
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


@overload
async def send_alert(
    channel: discord.TextChannel,
    title: str,
    description: str,
    name: str,
    avatar: str,
    files: None = None,
    fallback_file: str | BytesIO = path.join(path.dirname(__file__), FALLBACK_IMAGE),
) -> discord.Message: ...
@overload
async def send_alert(
    channel: discord.TextChannel,
    title: str,
    description: str,
    name: str,
    avatar: str,
    files: tuple[Optional[discord.File], Optional[discord.File]],
    fallback_file: str | BytesIO = path.join(path.dirname(__file__), FALLBACK_IMAGE),
) -> discord.Message: ...
async def send_alert(
    channel: discord.TextChannel,
    title: str,
    description: str,
    name: str,
    avatar: str,
    files: Optional[tuple[Optional[discord.File], Optional[discord.File]]] = None,
    fallback_file: str | BytesIO = path.join(path.dirname(__file__), FALLBACK_IMAGE),
) -> discord.Message | tuple[discord.Message, discord.Message]:
    embed = Embed(
        title=title,
        description=description,
        timestamp=datetime.now(),
        color=EMBED_DEFAULT_COLOR,
    )
    embed.set_author(
        name=name,
        icon_url=avatar,
    )
    main_message = await channel.send(embed=embed)

    # No files to also send
    if files is None:
        return main_message

    # TODO: Send as thumbnail instead
    if files[0] is None:
        files = (discord.File(fallback_file, "before.png"), files[1])

    if files[1] is None:
        files = (files[0], discord.File(fallback_file, "before.png"))

    return (
        main_message,
        await channel.send(files=cast(tuple[discord.File, discord.File], files)),
    )


async def check_alert_member(member: discord.Member):
    save, _ = get_save_from_guild(member.guild)

    if member.bot:
        return

    channel_id = get_key(save, "setting.channel")
    if channel_id is None:
        return

    channel = cast(discord.TextChannel, bot.get_channel(channel_id))
    if channel is None:
        return

    if get_key(save, ["members", str(member.id), "opt_out"]):
        return

    last_name: str | None = get_key(
        save, ["members", str(member.id), "last_seen", "display_name"]
    )
    last_pfp: str | None = get_key(
        save, ["members", str(member.id), "last_seen", "pfp"]
    )

    name_changed = last_name and last_name != member.display_name
    pfp_changed = last_pfp and last_pfp != member.display_avatar.url

    send_images = False

    alert_title: str = ""
    alert_description: str = ""

    if name_changed and pfp_changed:
        quip: str = choice(FUNNY_MESSAGES["common"] + FUNNY_MESSAGES["both"])

        alert_title = f"`{member.name}` changed there **name** and **avatar**!"
        alert_description = (
            f"## From `{last_name}` _(Before **Avatar** Left)_ ➡ "
            + f"`{member.display_name}` _(After **Avatar** Right)_)\n"
            + quip.format("name _AND_ profile picture")
        )

        send_images = True

    elif name_changed:
        quip: str = choice(FUNNY_MESSAGES["common"] + FUNNY_MESSAGES["name"])

        alert_title = f"`{member.name}` changed there **name**!"
        alert_description = (
            f"# From `{last_name}` ➡ `{member.display_name}`\n" + quip.format("name")
        )

    elif pfp_changed:
        quip: str = choice(FUNNY_MESSAGES["common"] + FUNNY_MESSAGES["avatar"])

        alert_title = f"`{member.name}` changed there **avatar**!"
        alert_description = (
            f"# `Before Avatar` _(Left)_ ➡ `After Avatar` _(Right)_\n"
            + quip.format("avatar")
        )

        send_images = True

    if name_changed or pfp_changed:
        print(
            f"DETECTED CHANGE IN USER {member.name} in guild "
            + f"{member.guild.id} ({member.guild.name})"
        )

        files: list[Optional[discord.File]] = [None, None]
        if send_images:
            try:
                files[0] = discord.File(
                    BytesIO(download_image(cast(str, last_pfp))),
                    "before.png",
                )
            except Exception as e:
                print(f"ERROR: COULD NOT DOWNLOAD FILE 0: '{last_pfp}'", e)

            try:
                files[1] = discord.File(
                    BytesIO(await member.display_avatar.read()),
                    "after.png",
                )
            except Exception as e:
                print(f"ERROR: COULD NOT READ FILE 1: '{member.display_avatar.url}'", e)

        await send_alert(
            channel,
            alert_title,
            alert_description,
            (last_name or member.display_name) + f" ({member.name})",
            last_pfp or member.display_avatar.url,
            files=(files[0], files[1]) if send_images else None,
        )

    save_guild_data(
        member.guild,
        {"display_name": member.display_name, "pfp": member.display_avatar.url},
        ["members", str(member.id), "last_seen"],
    )


if __name__ == "__main__":
    if not path.exists(".env"):
        raise FileNotFoundError(".env file dose not exist!")

    secrets = dotenv_values(".env")

    if "DISCORD_TOKEN" not in secrets:
        raise ValueError(".env must include a DISCORD_TOKEN!")

    intents = discord.Intents(
        guilds=True,
        members=True,
        guild_messages=True,
        message_content=True,
    )

    bot = Bot(command_prefix="!", intents=intents)

    @bot.check
    def check_guild():
        async def predicate(interaction: discord.Interaction):
            if interaction.guild is None:
                raise app_commands.NoPrivateMessage()

            return True

        return app_commands.check(predicate)

    def check_perms():
        async def predicate(interaction: discord.Interaction):
            bot_member = cast(discord.Guild, interaction.guild).me
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
        pre_key = ["members", str(interaction.user.id)]
        guild = cast(discord.Guild, interaction.guild)

        save, _ = get_save_from_guild(guild)
        already_opted_out: bool = get_key(save, pre_key + ["opt_out"]) or False
        if already_opted_out:
            await interaction.response.send_message(
                embed=Embed(
                    title="You are already opted out!",
                    description="Run `/optin` to opt back in.",
                    color=EMBED_ERROR_COLOR,
                ),
                ephemeral=True,
            )
            return

        with add_exception_notes("Could not save data because an error has occurred"):
            save_guild_data(guild, True, pre_key + ["opt_out"], create_keys=True)
            save_guild_data(guild, None, pre_key + ["last_seen"], create_keys=True)

        await interaction.response.send_message(
            embed=Embed(
                title="✔ You have successfully been opted in",
                description="Run `/optout` to opt out.",
                color=EMBED_DEFAULT_COLOR,
            ),
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
                embed=Embed(
                    title="You are already opted in!",
                    description="Run `/optout` to opt out.",
                    color=EMBED_ERROR_COLOR,
                ),
                ephemeral=True,
            )
            return

        with add_exception_notes("Could not save data because an error has occurred"):
            save_guild_data(guild, False, opt_out_key, create_keys=True)

        await interaction.response.send_message(
            embed=Embed(
                title="✔ You have successfully been opted in",
                description="Run `/optin` to opt back in.",
                color=EMBED_DEFAULT_COLOR,
            ),
            ephemeral=True,
        )

    @bot.tree.command(
        name="setchannel", description="Sets the channel for sending alerts."
    )
    @check_perms()
    async def setChannelCommand(
        interaction: discord.Interaction, channel: discord.TextChannel
    ):
        if channel.guild.id != cast(discord.Guild, interaction.guild).id:
            raise app_commands.CheckFailure(
                "Channel not in current server! Please enter a guild in this server."
            )

        with add_exception_notes("Could not save data because an error has occurred"):
            save_guild_data(
                channel.guild, channel.id, key="setting.channel", create_keys=True
            )

        await interaction.response.send_message(
            embed=Embed(
                title=f"✔ Successfully set output channel to {channel.jump_url}.",
                color=EMBED_DEFAULT_COLOR,
            ),
            ephemeral=True,
        )

    @bot.tree.command(
        name="testalert", description="Tests sending an alert to the chosen channel"
    )
    @check_perms()
    async def testAlert(interaction: discord.Interaction):
        save, _ = get_save_from_guild(cast(discord.Guild, interaction.guild))

        channel_id = get_key(save, "setting.channel")
        if channel_id is None:
            raise AppCommandError(
                "Channel save not set! Please run `/setchannel` to fix.",
            )

        channel = cast(discord.TextChannel, bot.get_channel(channel_id))
        if channel is None:
            raise AppCommandError(
                "Channel dose not exist! Please set a new one by running "
                + "`/setchannel`.",
            )

        alert = await send_alert(
            channel,
            "🚨 Test Alert 🚨",
            "This is a test alert 123",
            "PFP Alerter",
            cast(discord.User, bot.user).display_avatar.url,
        )

        await interaction.response.send_message(
            embed=Embed(
                title=f"Test completed successfully!",
                description=f"-# Jump to msg: {alert.jump_url}",
                color=EMBED_DEFAULT_COLOR,
            ),
            ephemeral=True,
        )

    @bot.event
    async def on_message(message: discord.Message):
        if not message.guild:
            return

        await check_alert_member(cast(discord.Member, message.author))

    @tasks.loop(minutes=5)
    async def check_alert_all_members():
        print("Mass checking and alerting all members in all guilds...")

        member_count = 0
        for guild in bot.guilds:
            for member in guild.members:
                await check_alert_member(member)
                member_count += 1

        print(
            f"Mass alert completed! Checked {member_count} members in"
            + f"{len(bot.guilds)} guilds."
        )

    # Error handling
    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction[Bot], error: AppCommandErrorBase
    ):
        embed = Embed(title="!ERROR!", color=EMBED_ERROR_COLOR)

        if isinstance(error, app_commands.NoPrivateMessage):
            embed.description = "🚫 This command can only be run in a server."
        elif isinstance(error, app_commands.MissingPermissions):
            embed.description = (
                "🚫 You don't have the required permissions to run this command."
            )
        elif isinstance(error, app_commands.MissingRole):
            embed.description = (
                f"🚫 You need the `{error.missing_role}` role to run this command."
            )
        elif isinstance(error, app_commands.TransformerError):
            embed.description = (
                "❗ Invalid value provided. Please check your input and try again."
            )
        elif isinstance(error, app_commands.CheckFailure):
            embed.description = (
                str(error)  # Default error message if non
                or "❌ You don't meet the requirements to use this command."
            )
        elif isinstance(error, AppCommandError):
            if not error.__notes__:
                await on_app_command_error(interaction, AppCommandErrorBase(error))

            embed.description = "\n".join(error.__notes__)
        else:
            tb = traceback.format_exc()
            embed.description = "An unknown error has occurred! " + ERROR_FOOTER
            await interaction.response.send_message(embed=embed, ephemeral=True)

            print(str(tb))
            # Fix for 2000 char max message
            # TODO: Send to log files and send log id instead
            split_traceback = split_length(str(tb), 1993)  # -7 characters for codeblock
            for trace_part in split_traceback:
                await interaction.followup.send(
                    "```" + trace_part + "\n```", ephemeral=True
                )

            return

        await interaction.response.send_message(embed=embed, ephemeral=True)

    bot.run(cast(str, secrets["DISCORD_TOKEN"]))
