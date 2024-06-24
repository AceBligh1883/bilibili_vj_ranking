import pandas as pd
import re

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
        print(bilibili_id)
        if bilibili_id.startswith('av'):
            av_number = int(bilibili_id[2:])
            return enc(av_number)
        elif bilibili_id.startswith('BV'):
            return bilibili_id
        elif bilibili_id.isdigit():
            av_number = int(bilibili_id)
            return enc(av_number)
        else:
            return 'BV'+bilibili_id
    elif isinstance(bilibili_id, int):
        return enc(bilibili_id)
    else:
        return bilibili_id

def main():
    # 读取Excel文件
    df = pd.read_excel('神话曲id.xlsx')

    # 转换Bilibili ID
    df['Bilibili ID'] = df['Bilibili ID'].apply(convert_id_to_bv)

    # 输出转换后的DataFrame
    print(df)

    # 保存到新的Excel文件
    df.to_excel('神话曲id_bv.xlsx', index=False)

if __name__ == "__main__":
    main()
