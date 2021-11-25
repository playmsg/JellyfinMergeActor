import requests
import json

GfriendsListUrl = 'https://raw.github.com/xinxin8816/gfriends/master/Filetree.json'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
}
GfriendsList = requests.get(GfriendsListUrl, headers=headers)
info = json.loads(GfriendsList.text)
jav = []
for i in info['Content']:
    content = info['Content'][i]
    for j in content:
        j = j.replace('.jpg', '')
        jav.append(j)

javStars = list(set(jav))
with open('gflist.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(javStars))
