#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) AFK

''' ----Adding Support of diffrent links---- '''


from main import LOGGER as LOGS, prefixes
from main import Config, Store
import datetime
import asyncio
import requests
import time
import base64
import re
import json
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL as ytdl


class ParseLink(object):
    def olive(Q, url, path):
        if not re.search("https://videos.sproutvideo.com/embed/.*/.*", url):
            print("\nThis does not seem like a valid type of url supported by the script. Follow the instructions on the README correctly and enter the embed link!")
        else:
            site_link = Store.SPROUT_URL  # "https://discuss.oliveboard.in/"

            try:
                domain_name = re.search(
                    'http.?://([A-Za-z_0-9.-]+).*', site_link).group(1)
            except Exception as e:
                print(f"\nError: {e}")
            else:
                proceed_further_1 = True

        if proceed_further_1:
            if "https" in site_link:
                referer_link = "https://" + domain_name + "/"
            else:
                referer_link = "http://" + domain_name + "/"

            headers = {
                'Referer': referer_link,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36}'
            }
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"\nError - Site Response:\n{response.text}")
                print("\n\nMake sure your links are correct!")
            else:
                print("\nA successful response has been issued!")
                try:
                    response_parts = response.text.split("var dat = '")
                    token = response_parts[1].split("'")[0]
                except Exception as e:
                    print(f"\nError: {e}")
                    LOGS.error(str(e))
                    # input("\nPress Enter to exit...")
                else:
                    proceed_further_2 = True

        if proceed_further_2:
            token_to_json = json.loads(
                base64.urlsafe_b64decode(token).decode('UTF-8'))
            video_name = token_to_json['title'].replace(
                "/", "").replace(":", "").strip()
            session_id = token_to_json['sessionID']
            cdn = token_to_json['base']
            sprout_host = token_to_json['analytics_host']
            user_hash = token_to_json['s3_user_hash']
            video_hash = token_to_json['s3_video_hash']

            m3u8_policy = token_to_json['signatures']['m']['CloudFront-Policy']
            m3u8_signature = token_to_json['signatures']['m']['CloudFront-Signature']
            m3u8_keypair_id = token_to_json['signatures']['m']['CloudFront-Key-Pair-Id']

            index_link = f"https://{cdn}.{sprout_host}/{user_hash}/{video_hash}/video/index.m3u8?Policy={m3u8_policy}&Signature={m3u8_signature}&Key-Pair-Id={m3u8_keypair_id}&sessionID={session_id}"

            qualities = requests.get(index_link).text.split("\n")
            print("\nAvailable Qualities :-\n")
            Qlty = []
            for i in qualities:
                if ".m3u8" in i:
                    quality = i.split(".m3u8")[0]
                    print(quality)
                    Qlty.append(quality)
                else:
                    continue
            if Q not in Qlty:
                Q = quality
            else:
                Q = Q
            Q_link = f"https://{cdn}.{sprout_host}/{user_hash}/{video_hash}/video/{Q}.m3u8?Policy={m3u8_policy}&Signature={m3u8_signature}&Key-Pair-Id={m3u8_keypair_id}&sessionID={session_id}"
            playlist_contents = requests.get(Q_link).text

            ts_policy = token_to_json['signatures']['t']['CloudFront-Policy']
            ts_signature = token_to_json['signatures']['t']['CloudFront-Signature']
            ts_keypair_id = token_to_json['signatures']['t']['CloudFront-Key-Pair-Id']

            ts_parts = re.findall(".*_.*ts", playlist_contents)
            for ts_part in ts_parts:
                ts_link = f"https://{cdn}.{sprout_host}/{user_hash}/{video_hash}/video/{ts_part}?Policy={ts_policy}&Signature={ts_signature}&Key-Pair-Id={ts_keypair_id}&sessionID={session_id}"
                playlist_contents = playlist_contents.replace(ts_part, ts_link)

            key_policy = token_to_json['signatures']['k']['CloudFront-Policy']
            key_signature = token_to_json['signatures']['k']['CloudFront-Signature']
            key_keypair_id = token_to_json['signatures']['k']['CloudFront-Key-Pair-Id']

            key_link = f"https://{cdn}.{sprout_host}/{user_hash}/{video_hash}/video/{Q}.key?Policy={key_policy}&Signature={key_signature}&Key-Pair-Id={key_keypair_id}&sessionID={session_id}"

            final_playlist = playlist_contents.replace(f"{Q}.key", key_link)

            full_title = video_name + "-" + str(Q) + "p"
            # file_to_download = full_title + ".m3u8"
            file_to_download = f"{path}/{full_title}.m3u8"
            try:
                with open(file_to_download, "a") as m3u8_writer:
                    m3u8_writer.write(final_playlist)
                    m3u8_writer.close()
            except Exception as e:
                LOGS.error(str(e))
                print(f"\nError: {e}")
        return file_to_download

    def vision_m3u8_link(link, Q):
        Q = str(Q)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'http://www.visionias.in/',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }
        response = requests.get(f'{link}', headers=headers)
        r = response.content
        soup = BeautifulSoup(r, 'html.parser')
        paras = soup.find('script')
        url = paras.text.split('"')[3]
        # URL = visio_url(url , Q)
        return url

    def vision_mpd_link(r_link):
        link = f'http://visionias.in/student/videoplayer_v2/video.php?{r_link.split("?")[-1]}'
        print(link)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'http://www.visionias.in/',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Mobile Safari/537.36',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }
        response = requests.get(f'{link}', headers=headers)
        r = response.content
        # r = open("vod.html")
        soup = BeautifulSoup(r, features="xml")
        res_link1 = soup.find_all("Location")[0].get_text()
        return res_link1


    def classplus_link(link):
        headers = {
            'Host': 'api.classplusapp.com',
            'x-access-token': Store.CPTOKEN,
            'user-agent': 'Mobile-Android',
            'app-version': '1.4.37.1',
            'api-version': '18',
            # 'accept-encoding': 'gzip',
        }
        response = requests.get(
            f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={link}', headers=headers)
        url = response.json()['url']
        print(url)
        return url

    def is_pw(url):
        """
        Sample Link :- https://d1d34p8vz63oiq.cloudfront.net/8eca5705-a305-4c1d-863f-a5b101c1983a/master.m3u8
        """
        r_code = requests.get(url=url)
        print(r_code)
        if r_code.status_code != 200:
            link = f'https://d3nzo6itypaz07.cloudfront.net/{url.split("/")[3]}/master.m3u8'
            print(link)
            r_code1 = requests.get(url=link)
            if r_code1.status_code == 200:
                return link
        else:
            link = url
            return link
        
    
    def topranker_link(url: str):
        host = f"https://{url.split('/')[2]}"
        _id = url.split('/')[-1].split('-')[0]
        print(host)
        r = requests.post(f"{host}/route?route=item%2Fliveclasses&id={_id}&response-type=2&fromapp=1&loadall=1&clientView=1&liveFromCDN=1&clientVersion=1.9").json()
        if None == r['data']['tr1info']['primPlaybackUrl']:
            ytid =r['data']['tr1info']['data']['youtubeId']
            link = f'https://www.youtube.com/watch?v={ytid}'
        else:
            link = r['data']['tr1info']['primPlaybackUrl']
        LOGS.info(link)
        return link

    def rout(url, m3u8):
        rout_link = f'https://{url.split("/")[2]}/?route=common/ajax&mod=liveclasses&ack=getcustompolicysignedcookiecdn&stream={"/".join(m3u8.split("/")[0:-1]).replace("/", "%2F").replace(":", "%3A")}master.m3u8'
        LOGS.info(rout_link)
        return rout_link

    def is_drive_pdf(url):
        if url.startswith('https://drive.google.com/') and ("file" or "open" or "sharing" or "view" or "/d" in url):
            print("Drive link", True)
            _id = url.split('/')[5]
            res = f"https://drive.google.com/uc?export=download&id={_id}"
            LOGS.info(res)
            return res
        else:
            return  url

    def cw_url2(class_id):
        ACCOUNT_ID = "6206459123001"
        BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
        BC_URL = (
            f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos"
        )
        BC_HDR = {"BCOV-POLICY": BCOV_POLICY}
        video_response = requests.get(f"{BC_URL}/{class_id}", headers=BC_HDR)
        video = video_response.json()
        # print(video["sources"])
        try:
            video_source = video["sources"][5]
            video_url = video_source["src"]
        except IndexError:
            video_source = video["sources"][1]
            video_url = video_source["src"]
        return video_url