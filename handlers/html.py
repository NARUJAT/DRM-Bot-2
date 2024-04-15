from bs4 import BeautifulSoup
import os

def parse_html(file):
    with open(file, "r") as f:
        source = f.read()

    soup = BeautifulSoup(source, "html.parser")

    info = soup.select_one("p#info")
    mg_info = soup.select_one("p[style='text-align:center;font-size:30;color:Blue']")
    buttons_soup = soup.select("button.collapsible")
    paras_soup = soup.select("p")[2:]
    if info is not None:
        all_videos_soup = soup.select_one("div#videos")
        topics_soup = all_videos_soup.select("div.topic")
        videos = []
        for topic_soup in topics_soup:
            topic_name = topic_soup.select_one("span.topic_name").get_text(strip=True)
            videos_soup = topic_soup.select("p.video")
            for video_soup in videos_soup:
                video_name = video_soup.select_one("span.video_name").get_text(
                    strip=True
                )
                video_link = video_soup.select_one("a").get_text(strip=True)
                if not (
                    video_link.startswith("http://")
                    or video_link.startswith("https://")
                ):
                    continue

                videos.append(f"{video_name.replace(':', '')}:{video_link}".split(':',1))
    elif mg_info is not None and len(buttons_soup) != 0:
        videos = []
        for button_soup in buttons_soup:
            topic_name = button_soup.get_text(strip=True).strip("Topic :- ")
            para = button_soup.find_next_sibling("div", class_="content").p
            # ps = [para.contents[i] for i in range(0,len(para)) if i%5==0 ]
            for a_soup in para.select("a"):
                br = a_soup.find_previous_sibling()
                br.decompose()
                video_name = a_soup.previousSibling
                video_link = a_soup.get_text(strip=True)
                if not (
                    video_link.startswith("http://")
                    or video_link.startswith("https://")
                ):
                    continue
                videos.append(f"{video_name.replace(':', '')}:{video_link}".split(':',1))
    elif mg_info is not None and paras_soup[0].b is not None:
        videos = []
        for topic_para in paras_soup:
            if paras_soup.index(topic_para) % 2 == 0:
                topic_name = topic_para.get_text(strip=True).strip("Topic :- ")
                para = topic_para.find_next_sibling("p")
                for a_soup in para.select("a"):
                    br = a_soup.find_previous_sibling()
                    br.decompose()
                    video_name = a_soup.previousSibling
                    video_link = a_soup.get_text(strip=True)
                    if not (
                        video_link.startswith("http://")
                        or video_link.startswith("https://")
                    ):
                        continue
                    videos.append(
                        f"{video_name.replace(':', '')}:{video_link}".split(':',1)
                    )
            else:
                continue
    elif (
        mg_info is not None
        and paras_soup[0].get("style") == "text-align:center;font-size:25px;"
    ):
        topic_name = ""
        videos = []
        for para in paras_soup:
            video_name = para.contents[0]
            video_link = para.select_one("a").get_text(strip=True)
            if not (
                video_link.startswith("http://")
                or video_link.startswith("https://")
            ):
                continue
            videos.append(f"{video_name.replace(':', '')}:{video_link}".split(':',1))
    else:
        videos = []
        topic_name = ""
        video_name = ""
        for a_soup in soup.select("a"):
            video_link = a_soup.get("href")
            if not (
                video_link.startswith("http://")
                or video_link.startswith("https://")
            ):
                continue
            videos.append(f"{video_name.replace(':', '')}:{video_link}".split(':',1))
    
    return videos