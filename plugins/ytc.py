from pyrogram import filters, Client as ace
from main import LOGGER as LOGS, prefixes
from pyrogram.types import Message
from main import Config
import os
import subprocess
import tgcrypto
import shutil
import sys
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient
import requests
import wget
import img2pdf

@ace.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("ytc", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/PHOTO/{m.chat.id}"
    os.makedirs(path, exist_ok=True)
    os.makedirs(tPath, exist_ok=True)

    pages_msg = await bot.ask(m.chat.id, "Send Pages Range Eg: '1:100'\nBook Name\nBookId")
    pages, Book_Name, bid = str(pages_msg.text).split("\n")

    url = "http://yctpublication.com/master/api/MasterController/getPdfPage?book_id={bid}&page_no={pag}&user_id=14593&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjVkZjFmOTQ1ZmY5MDZhZWFlZmE5M2MyNzY5OGRiNDA2ZDYwNmIwZTgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMjkwMDE2MzYyNTQtZWZjcDlqYm4wMzJzbmpmc"
    page = pages.split(":")
    page_1 = int(page[0])#1
    last_page = int(page[1])+1 # Total Page se Ek Jayda Hi rakhna hai

    def download_image(image_link, file_name):
        k = requests.get(url=image_link)
        print(k.status_code)
        with open(f"{tPath}/{file_name}.jpg", "wb") as f:
            f.write(k.content)
        return f"{tPath}/{file_name}.jpg"

    def down(image_link, file_name):
        wget.download(image_link, f"{tPath}/{file_name}.jpg")
        return f"{tPath}/{file_name}.jpg"


    def downloadPdf(title, imagelist):
        with open(f"{path}/{title}.pdf", "wb") as f:
            f.write(img2pdf.convert([i for i in imagelist]))
        PDF = f"{path}/{title}.pdf"
        return PDF

    Show =  await bot.send_message(
        m.chat.id,
        "Downloading"
    )
    IMG_LIST = []

    for i in range(page_1, last_page):
        # print(url.format(i))
        try:
            print(f"Downloading Page - {str(i).zfill(3)}")
            name = f"{str(i).zfill(3)}. page_no_{str(i)}"
            y = down(image_link=url.format(pag = i, bid= bid), file_name=name)
            IMG_LIST.append(y)
        except Exception as e:
            await m.reply_text(str(e))
            continue
    try:
        PDF = downloadPdf(title=Book_Name, imagelist=IMG_LIST)
    except Exception as e1:
        await m.reply_text(str(e1))
    Thumb = "hb"
    UL = Upload_to_Tg(bot=bot, m=m, file_path=PDF, name=Book_Name,
                        Thumb=Thumb, path=path, show_msg=Show, caption=Book_Name)
    await UL.upload_doc()
    print("Done")
    shutil.rmtree(tPath)
    
