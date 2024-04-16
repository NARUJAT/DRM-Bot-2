#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) AFK

import os
import subprocess
import datetime
import asyncio
import wget
import requests
import time
import aiohttp
import tgcrypto
import aiofiles
import sys
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from main import Config


class Tools(object):
    def duration(filename):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return float(result.stdout)

    async def aio(url, name, path):
        k = f"{path}/{name}.pdf"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(k, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
        return k

    def vid_info(info):
        info = info.strip()
        info = info.split("\n")
        new_info = dict()
        temp = []
        for i in info:
            i = str(i)
            if "[" not in i and '---' not in i:
                while "  " in i:
                    i = i.replace("  ", " ")
                i.strip()
                i = i.split("|")[0].split(" ", 3)
                try:
                    if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                        temp.append(i[2])
                        new_info.update({f'{i[2]}': f'{i[0]}'})
                except:
                    pass
        return new_info

    async def vrun(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        print(f'[{cmd!r} exited with {proc.returncode}]')
        if proc.returncode == 1:
            return False
        if stdout:
            return f'[stdout]\n{stdout.decode()}'
        if stderr:
            return f'[stderr]\n{stderr.decode()}'

    def old_download(url, file_name, chunk_size=1024 * 10):
        if os.path.exists(file_name):
            os.remove(file_name)
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        return file_name

    def human_readable_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0 or unit == 'PB':
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"

    def time_name():
        date = datetime.date.today()
        now = datetime.datetime.now()
        current_time = now.strftime("%H : %M : %S")
        return f"📅 **Date** ~ `{date}`\n🕰 **Time** ~ `{current_time}`"

    def convert(seconds):
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    async def pdf_thumb(Thumb, name, path):
        if Thumb.startswith(("http://", "https://")):
            wget.download(Thumb, f"{path}/{name}.jpg")
            pdfthumb = f"{path}/{name}.jpg"
        else:    
            wget.download("https://telegra.ph/file/84870d6d89b893e59c5f0.jpg", f"{path}/{name}.jpg")
            pdfthumb = f"{path}/{name}.jpg"
        return pdfthumb

class Vidtools(object):
    async def take_screen_shot(video_file, name, path, ttl):
        out_put_file_name = f"{path}/{name}.jpg"
        if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
            file_genertor_command = [
                "ffmpeg",
                "-ss",
                str(ttl),
                "-i",
                video_file,
                "-vframes",
                "1",
                out_put_file_name
            ]
            process = await asyncio.create_subprocess_exec(
                *file_genertor_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()

        if os.path.lexists(out_put_file_name):
            return out_put_file_name
        else:
            return None

    def get_duration(filepath):
        metadata = extractMetadata(createParser(filepath))
        if metadata.has("duration"):
            return metadata.get('duration').seconds
        else:
            return 0

    async def get_width_height(filepath):
        metadata = extractMetadata(createParser(filepath))
        if metadata.has("width") and metadata.has("height"):
            return metadata.get("width"), metadata.get("height")
        else:
            return 1280, 720


