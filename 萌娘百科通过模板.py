import requests
import re
import pandas as pd
from bilibili_api import video
import asyncio

template = "虚拟歌手歌曲荣誉题头"
url = "https://moegirl.icu/api.php"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    # 可以根据需要添加更多的UA字符串
]

user_agent = "VirtualSingerDatabase/0.1 (759723417@qq.com)"
headers = {"User-Agent": user_agent}

#AV和BV互转函数部分
table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr={}
for i in range(58):
	tr[table[i]]=i
s=[11,10,3,8,4,6]
xor=177451812
add=8728348608

def dec(x):
	r=0
	for i in range(6):
		r+=tr[x[s[i]]]*58**i
	return (r-add)^xor

def enc(x):
	x=(x^xor)+add
	r=list('BV1  4 1 7  ')
	for i in range(6):
		r[s[i]]=table[x//58**i%58]
	return ''.join(r)

def convert_id_to_bv(bilibili_id):
    if isinstance(bilibili_id, str):
        if bilibili_id.startswith('av'):
            av_number = int(bilibili_id[2:])
            return enc(av_number)
        elif bilibili_id.startswith('BV'):
            return bilibili_id
        elif bilibili_id.startswith('bv'):
            return bilibili_id.replace('bv', 'BV')
        elif bilibili_id.isdigit():
            av_number = int(bilibili_id)
            return enc(av_number)
        elif len(bilibili_id)==10:
            return 'BV'+bilibili_id
        else:
            return None
    elif isinstance(bilibili_id, int):
        return enc(bilibili_id)
    else:
        return None

#以下正式开始
def get_pages_linking_to_template(template):
    params = {
        "action": "query",
        "list": "embeddedin",
        "eititle": "Template:" + template,
        "eilimit": "max",
        "einamespace": "0",
        "format": "json"
    }
    
    all_pages = []
    while True:
        response = requests.get(url, params=params, headers=headers)
        print(response)
        data = response.json()
        
        pages = data.get("query", {}).get("embeddedin", [])
        all_pages.extend([page["title"] for page in pages])
        
        if "continue" in data:
            params["eicontinue"] = data["continue"]["eicontinue"]
        else:
            break
    
    return all_pages

def get_page_content(title):

    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "format": "json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    page_id = next(iter(data["query"]["pages"]))
    page_content = data["query"]["pages"][page_id]["revisions"][0]["*"]
    return page_content

def extract_bilibili_id(content):
    # Match both {{BilibiliVideo|id=xxxxxx}} and {{bilibilivideo|id=xxxxxx}}
    match = re.search(r"\{\{[Bb]ilibili[Vv]ideo\s*(\|[^{}]*)*?\|id=(.+?)(\|[^{}]*)*?\}\}", content)
    if match:
        return match.group(2).strip()
    else:
        match = re.search(r"\{\{bv\s*\|*?\|(.+?)(\|[^{}]*)*?\}\}", content)
        if match:
            return match.group(1).strip()
    return None

async def get_video_data(bvid):
    v = video.Video(bvid=bvid)
    try:
        info = await v.get_info()  
    except Exception as e:
        print(e)
        return None, None
    stat_data = info.get('stat')  # 提取stat字段的数据  
    if stat_data:  
        name = info.get('title')
        view = stat_data.get('view')
    return name, view

async def main():
    
    pages = get_pages_linking_to_template(template)
    data = {
        "Title": [],
        "BVID": [],
        "Video Title": [],
        "View": []
    }
    for title in pages:
        print(title, end=" ")
        content = get_page_content(title)
        bilibili_id = extract_bilibili_id(content)
        bvid = convert_id_to_bv(bilibili_id)
        if bvid:
            print(bvid)
            video_title, view = await get_video_data(bvid)
            data["Title"].append(title)
            data["BVID"].append(bvid)
            data["Video Title"].append(video_title)
            data["View"].append(view)
    
    df = pd.DataFrame(data)
    # 转换Bilibili ID
    df.to_excel(f'视频id/{template}_id.xlsx', index=False)

if __name__ == "__main__":
    asyncio.run(main())
