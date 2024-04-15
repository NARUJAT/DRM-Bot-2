
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) AFK

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import subprocess
import wget
import os
import time
import requests
import asyncio
import datetime
from helpers.toolkit import Tools, Vidtools
from main import Config, Msg, Store, LOGGER as LOGS
from helpers.prog_bar import progress_for_pyrogram
from pyrogram import Client as AFK
from pyrogram.types import Message


class Upload_to_Tg:
    def __init__(self, bot: AFK, m: Message, name: str, file_path, path, Thumb, show_msg: Message, caption: str) -> None:
        self.bot = bot
        self.m = m
        self.name = name
        self.file_path = file_path
        self.path = path
        self.thumb = Thumb
        self.temp_dir = f"{path}/{name}"
        self.show_msg = show_msg
        self.caption = caption

    async def get_thumb_duration(self):
        try:
            duration = Vidtools.get_duration(self.file_path)
        except:
            duration = int(Tools.duration(self.file_path))

        if self.thumb.startswith(("http://", "https://")):
            wget.download(self.thumb, f"{self.temp_dir}.jpg")
            thumbnail = f"{self.temp_dir}.jpg"
        elif os.path.isfile(self.thumb):
            thumbnail = self.thumb
        else:
            try:
                thumbnail = await Vidtools.take_screen_shot(self.file_path, self.name, self.path, (duration / 2))
            except:
                subprocess.run(
                    f'ffmpeg -i "{self.filename}" -ss 00:00:01 -vframes 1 "{self.temp_dir}.jpg"', shell=True)
                thumbnail = f"{self.temp_dir}.jpg"
        return duration, thumbnail

    async def get_doc_thumb(self):
        if self.thumb.startswith(("http://", "https://")):
            wget.download(self.thumb, f"{self.temp_dir}.jpg")
            doc_thumbnail = f"{self.temp_dir}.jpg"
        elif os.path.isfile(self.thumb):
            doc_thumbnail = self.thumb
        else:
            # wget.download(Extra_info.THUMB_URL, f"{path}/{name}.jpg")
            # doc_thumbnail = f"{path}/{name}.jpg"
            doc_thumbnail = None
        return doc_thumbnail

    async def upload_video(self):
        duration, thumbnail = await Upload_to_Tg.get_thumb_duration(self)
        w, h = await Vidtools.get_width_height(self.file_path)
        start_time = time.time()
        try:
            await self.bot.send_video(
                chat_id=self.m.chat.id,
                video=self.file_path,
                supports_streaming=True,
                caption=self.caption,
                duration=duration,
                thumb=thumbnail,
                width=w,
                height=h,
                progress=progress_for_pyrogram,
                progress_args=(
                    Msg.CMD_MSG_2.format(
                        file_name=f"{self.name}"), self.show_msg, start_time
                )
            )
        except Exception as e:
            LOGS.error(str(e))
            await self.bot.send_document(
                chat_id=self.m.chat.id,
                document=self.file_path,
                caption=self.caption,
                thumb=thumbnail,
                progress=progress_for_pyrogram,
                progress_args=(
                    Msg.CMD_MSG_2.format(
                        file_name=f"{self.name}"), self.show_msg, start_time
                )
            )
        os.remove(self.file_path)
        await self.show_msg.delete(True)

    async def upload_doc(self):
        start_time = time.time()
        try:
            await self.bot.send_document(
                chat_id=self.m.chat.id,
                document=self.file_path,
                caption=self.caption,
                thumb=await Upload_to_Tg.get_doc_thumb(self),
                progress=progress_for_pyrogram,
                progress_args=(
                    Msg.CMD_MSG_2.format(
                        file_name=f"{self.name}"), self.show_msg, start_time
                )
            )
        except Exception as e:
            LOGS.info(str(e))
        os.remove(self.file_path)
        await self.show_msg.delete(True)
