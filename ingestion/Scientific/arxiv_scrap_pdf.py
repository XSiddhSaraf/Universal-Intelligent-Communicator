from bs4 import BeautifulSoup
import requests
from pdfminer.high_level import extract_text
import os, time

# with open('simple.html') as html_file:
#     soup = BeautifulSoup(html_file, 'lxml')
start_time = time.time()

def extract_pdfs():
    source = requests.get('https://arxiv.org/list/cs.LG/recent').text
    soup = BeautifulSoup(source, 'lxml')

    #print(soup.prettify())

    page = soup.find('div', id='content')
    #print(page.prettify())

    pdf_1 = page.find('dl')
    pdf_link = pdf_1.find_all('span', class_='list-identifier')

    i = 0

    base_url = 'https://arxiv.org'
    print("Current working directory before")
    print(os.getcwd())
    print('Changing path to save PDF fles..'+'to:')
    os.chdir('scrapped_pdfs')
    print(os.getcwd())


    for anchor in pdf_link:
        pdf_url = anchor.find(title="Download PDF").get('href')
        pdfs = base_url+pdf_url
        i = i+1
        new_file_name = 'machine_learning_'+str(i)
        response = requests.get(pdfs)
        pdf = open(new_file_name + ".pdf", 'wb')
        pdf.write(response.content)
        pdf.close()
        print("File ", new_file_name, " downloaded")


def read_pdf(filename):
    os.chdir('scrapped_pdfs')
    pathl = '\scrapped_pdfs'
    if os.getcwd().endswith(pathl):
        print('File found...')
        print(extract_text(filename+'.pdf'))
        os.chdir('../')
    else:
        print('Path is wrong..')
        print(os.getcwd())


time.sleep(1)
end_time = time.time()

time.sleep(1)
#extract_pdfs()
print('Time taken :', start_time-end_time)

read_pdf('machine_learning_5')