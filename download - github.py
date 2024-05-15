import re
import math
import time
import requests

def extract_content(json_data):
    # 提取内容并将其格式化为文本

    replies = json_data.get('Replies', [])  # 回复列表

    # 遍历每个回复，提取内容并在每个内容前添加对应的 "now" 值
    formatted_content = ''
    for reply in replies:
        now_value = reply.get('now', '')  # 获取 "now" 值
        user_hash = reply.get('user_hash', '')  # 用户哈希值
        reply_content = reply.get('content', '')
        if reply_content:
            formatted_content += "时间：" + now_value + "  " + "ID:" + user_hash + '\n' + reply_content + '\n\n'

    # 去掉 HTML 标签并转换为文本格式
    formatted_content = re.sub(r'<.*?>', '', formatted_content)
    formatted_content = formatted_content.replace('<br>', '\n')  # 将 <br> 替换为换行符

    return formatted_content

def download_thread(thread_id, po_only):
    # 下载主题内容的函数

    base_url = 'https://api.nmb.best/api/'
    if po_only:
        url_template = base_url + 'po/thread?id={}&page={}'
    else:
        url_template = base_url + 'thread?id={}&page={}'

    cookies = {'userhash': ''}  # 用你实际的用户哈希值替换

    try:
        response = requests.get(url_template.format(thread_id, 1), cookies=cookies)
        response.raise_for_status()

        json_data = response.json()
        reply_count = json_data.get('ReplyCount')
        pages = math.ceil(reply_count / 19)

        print("需要下载的总页数:", pages)

        for page_num in range(1, pages + 1):
            response = requests.get(url_template.format(thread_id, page_num), cookies=cookies)
            response.raise_for_status()

            json_data = response.json()
            formatted_content = extract_content(json_data)

            if page_num == 1:
                # 当页数为1时，创建一个新的文本文件并写入内容
                with open('thread_content.txt', 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                    print(formatted_content)
            else:
                # 当页数不为1时，追加内容到已有文本文件中
                with open('thread_content.txt', 'a', encoding='utf-8') as f:
                    f.write(formatted_content)
                    print(formatted_content)

            time.sleep(1)  # 限制速率，避免过于频繁地请求服务器

        print("下载完成。")

    except requests.RequestException as e:
        print("请求失败:", e)

if __name__ == "__main__":
    thread_id = input("请输入串号: ")
    po_only = input("是否仅下载 Po？(y/n): ").lower() == 'y'

    download_thread(thread_id, po_only)
