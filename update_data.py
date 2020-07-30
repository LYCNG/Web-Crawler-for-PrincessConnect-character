import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import re

DRIVER = 'D:\TOOL\chromedriver.exe'
options = webdriver.ChromeOptions()
options.headless = True #加這行會在後台執行
driver = webdriver.Chrome(DRIVER, options=options)


#取得角色資訊並整理
class update():
    def __init__(self,char,id_list):
        self.id = id_list
        self.get_char(char,self.id)

    def get_soup(self,char):#get the 圖書館的某位腳色的html
        driver.get("https://pcredivewiki.tw/Character/Detail/" + str(char))
        html_text=driver.page_source 
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup

    def info(self,soup):
        list_da = [i.text for i in soup.table.find_all('th')]#get the value in the <th> i.text 可以將<>內容</>取出來
        list_va = [i.text for i in soup.table.find_all('td')]#get the value in the <td>
        dic = {}
        for x in range(10):
            dic[str(list_da[x])] = str(list_va[x])
        return dic

    def pic(self,soup):#get the src='url' of picture of character's html 
        return "https://pcredivewiki.tw"+str(soup.find("img",class_="d-block mx-auto img-fluid chara-thumb-img").get('src'))

    def discrib(self,soup):#get the discription of character's html
        return [i for i in soup.find('span',class_ = "my-3 d-block")][1]

    def skill(self,soup):
        skill_dict = {}
        fullskill = soup.find_all('div',class_ = "skill-description")
        for skill in fullskill:
            m = re.match(r"(\S*) (.*)",skill.text)
            skill_dict[m.group(1)] = m.group(2)
        return skill_dict

    def get_un(self,soup):
        #檢查該角色有無專武 沒有則回傳None
        if soup.find('div',class_ = "prod-info-box unique mb-3"):
            u = soup.find('div',class_ = "prod-info-box unique mb-3")
            un = u.find_all("span",class_="title")
            un_value = u.find_all("span",class_="prod-value")
            un_p = u.find("img")
            un_dic ={
                "un_name":u.find("h2").text,
                "un_discrib":u.find("p").text,
                "un_p":un_p.get("src")
                }
            for tup in list(zip(un,un_value)):
                un_dic[tup[0].text] = tup[1].text
            return un_dic
        else:
            return 0
            
    def get_char(self,char,idlist):
        with open('lib//chardata.json','r',encoding = 'utf-8') as load_check:
            char_dic = json.load(load_check)
            soup = self.get_soup(char)#取得腳色的soup
            discrib = self.discrib(soup)#get discription from soup
            pic = self.pic(soup)#get pic src from soup
            info = self.info(soup)#get char data from soup
            skill = self.skill(soup)#get skill of char from soup
            charid = idlist[char]#get char id 
            un_data = self.get_un(soup)#get char unique weapon if she has
            char_dic[char]={
                "discrib":str(discrib),
                'img':pic,
                'info':info,
                'nick':[],
                'skill':skill,
                'id':charid,
                "un":un_data
                        }
        with open('lib//chardata.json','w',encoding = 'utf-8') as dump_f:
            json.dump(char_dic,dump_f,ensure_ascii=False)# ensure_ascii=False 直接寫入字串，不會把他們轉成ascii
        return 'finish'

#取得腳色在圖書館的id
class char_update():
    def __init__(self):
        self.charlist

    def soup(self):
        driver.get("https://pcredivewiki.tw/Character")
        soup = BeautifulSoup(driver.page_source , 'html.parser')
        return soup

    #擷取所有角色
    def charlist(self):
        soup = self.soup()
        char_list = [i.text for i in soup.find_all('small')]
        return char_list

    #取得角色的id
    def get_id(self):
        soup = self.soup()
        def get_photo():
            photolist=[]
            photo = [str(i) for i in soup.find_all('div',class_="card")]
            for n in photo:
                num = re.findall(r"_(\d*)",re.search(r"src=+(.*)/>",n).group(1))
                photolist.append(num[1])
            return photolist

        def matchlist(list1,list2):
            char_id_li = list(zip(list1,list2))
            char_id_dic = {char[0]:char[1] for char in char_id_li}
            return char_id_dic
        return matchlist(self.charlist(),get_photo())
    
#整理角色星數配對
class sort():
    def soup(self):
        driver.get("https://pcredivewiki.tw/Character")
        soup = BeautifulSoup(driver.page_source , 'html.parser')
        return soup

    def star(self):
        soup =self.soup()
        soup1 = soup.find('div',class_="pb-3 lg-pt-3 d-flex flex-wrap justify-content-center justify-content-lg-start")
        three = len(soup1.find_all('div',class_="m-2 c-box anm-float"))
        a = [i.text for i in soup.find_all('small')]
        b = {}
        for char in a[:three]:
            b[char] = "3"
        for char in a[three:three+21]:
            b[char] ="2"
        for char in a[three+21:]:
            b[char] = '1'
        return b

    def input_data(self):
        b = self.star()
        with open('lib//chardata.json','r',encoding = 'utf-8') as load_check:
            char_dict = json.load(load_check)

        for char1 in list(char_dict.keys()):
            if char1 in list(b.keys()):
                char_dict[char1]['star'] = b[char1]
            else:
                pass
        with open('lib//chardata.json','w',encoding = 'utf-8') as dump_f:
            json.dump(char_dict,dump_f,ensure_ascii=False)
            
        return 'finish'

#取出資料庫的角色
with open('lib//chardata.json','r',encoding = 'utf-8') as get_data:
    orchar_data = json.load(get_data)

def run():
    #比對抓下來的角色和資料庫的角色，如果有不在內的角色就跑update
    char_list = char_update().charlist()
    id_list = char_update().get_id()
    for character in char_list:
        if character not in orchar_data:
            update(character,id_list)
            print('updated '+character)
        else:
            pass
    return sort().input_data()

#角色專武圖片的key現在是 up_p 之後改成 un_p //char.py的get_un要記得改!!!!

#刪除舊版本的角色
old =["安"]
def removeold(list):
    with open('lib//chardata.json','r',encoding = 'utf-8') as load_check:
        char_dict = json.load(load_check)
    for name in old:
        del char_dict[name]
        print('delete '+name)
    with open('lib//chardata.json','w',encoding = 'utf-8') as dump_f:
        json.dump(char_dict,dump_f,ensure_ascii=False)
    

#removeold(old)
run()