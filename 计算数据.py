import asyncio  
import pandas as pd  
from datetime import datetime  


old_file = '20240620215908'
new_file = '20240621110530'

async def main() -> None:  
    songs = pd.read_excel('收录曲目.xlsx')
    bv = songs.BVID
 
    info_list = []  # 用于存储视频信息的列表  
    old_data = pd.read_excel(f'数据/{old_file}.xlsx')
    new_data = pd.read_excel(f'数据/{new_file}.xlsx')
    for bvid in bv:  
        if not bvid:  
            continue  
        try:  
            new = new_data[new_data['bvid'] == bvid].iloc[0]
            old = old_data[old_data['bvid'] == bvid].iloc[0]
            name = new['title']
            view = new['view'] - old['view']
            favorite = new['favorite'] - old['favorite']
            coin = new['coin'] - old['coin']
            share = new['share'] - old['share']
            like = new['like'] - old['like']
            danmaku = new['danmaku'] - old['danmaku']
            reply = new['reply'] - old['reply']
            point = view + favorite*20 + coin*10 + share*10 + like*10
            info_list.append([bvid, name, view, favorite, coin, share, like, point])  
            
        except Exception as e:
            print(f"Error fetching info for BVID {bvid}: {e}")  

    # 将列表转换为Pandas DataFrame并保存为Excel文件  
    if info_list:  # 确保info_list不为空  
        stock_list = pd.DataFrame(info_list, columns=['bvid', 'name', 'view', 'favorite', 'coin', 'share', 'like', 'point'])  
        stock_list = stock_list.sort_values('point', ascending=False)
        filename = f"差异/{new_file}与{old_file}.xlsx"
        stock_list.to_excel(filename, index=False)  
        print("处理完成，数据已保存到", filename)  

  
if __name__ == "__main__":  
    asyncio.run(main())
