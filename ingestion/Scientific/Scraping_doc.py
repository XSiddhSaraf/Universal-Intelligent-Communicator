from bs4 import BeautifulSoup
import requests
import re
import urllib
arxiv_url = "https://arxiv.org"
r = requests.get(arxiv_url)

soup = BeautifulSoup(r.content)
urls =[]
url_get =[]
true_url=[]
url_details =[]
article_id = []
#print(soup.find_all("a"))

for link in soup.find_all("a"):
    urls.append(link.get("href"))
    url_details.append(link.text)


list_of_interest =['/archive','/list','/search',]
# list_http_word = ["http","https"]
word_re = re.compile("|".join(list_of_interest))


for item in urls:
    if word_re.search(item):
        url_get.append(item)

# create url to visit by adding suffix of stream and original Arxiv base url
def create_url_for_pdf(url_suffix):
    for suffix in url_suffix:
        true_url.append(arxiv_url+suffix)
    return true_url

url_extend = create_url_for_pdf(url_get)

#TODO Find article id from the web url obtained in aboe List called url_extend
#TODO Try to remove the list item which contains a http url link as it's causing exception
#TODO In below finction try to get the article id by inspect element of the page as there is a subsequent href link which contains article id number
#TODO this article id is required to pull pdf files since the url for download is base_url/pdf/articleid

#Extract article id
def extraxt_article_id(url_with_base):
    for each_url in url_with_base:
        res = requests.get(each_url)
        soup_nxt = BeautifulSoup(res.content)
        g_data = soup_nxt.find_all("div",{"class:list-identifier"})
    return g_data

article_id_url =extraxt_article_id(url_extend)
print(article_id_url)



# Trying to use urllin to extract pdf
# def extract_pdf(urls):
#     no=1
#     for url_item in urls:
#         urllib.url_retrive(url_item,"/Users/siddharthsaraf/Arxiv_docs/{file_name)".format(no))







