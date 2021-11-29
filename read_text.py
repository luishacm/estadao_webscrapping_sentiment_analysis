import pytesseract
from PIL import Image
import time
from nltk.tokenize import sent_tokenize
import pandas as pd
import os

#Select the correct path for your Tesseract instalation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

#Selecting True for this variable will only get the text from an image, clean it and save it in the database
#Selecting False for this variable will also ask you the sentiments of the text for each of its paragraphs
only_clean = False

#If you started determining the sentiment of the texts and closed the program this will help.
#If choose this variable as True it will restart where you left last
#However, you should always finish determining the sentiment of all the paragraphs of the same Article and stop at the start of the next article
#Or else, it won't save the unfinished analysis of that article.
restart_where_stoped = True

#This function will transform the image given to it in text
#It will return the raw reading
def read_text(path):
##    img = cv2.imread(path)
##    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
##    ret,thresh1 = cv2.threshold(gray, 0, 255,cv2.THRESH_OTSU|cv2.THRESH_BINARY_INV)
##    im = Image.fromarray(thresh1)
    im = Image.open(path)
    text = pytesseract.image_to_string(im, lang = 'por', config="--psm 3 --oem 3")
    return text

#This function will receive the Text and then clean it accordingly
#Will remove unnecessary spaces, join words that were separated and separate each sentence in a different item of a list
#It will return a list with each sentence inside
def clean_text(text):
    new_lista = []
    index_lista = []
    final_text = []
    for i in text:
        new_lista.append(i)
    for i, j in enumerate(new_lista):
        if j == "-":
            index_lista.append(i)
    final_text = text
    x = 0
    for i in index_lista:
        final_text = final_text[:i-x] + final_text[i-x+2:]
        x += 2            
    final_text = sent_tokenize(final_text)
    final_lista = []
    for i in final_text:
        repeat = 0
        lista = []
        for o in i:
            if o == '\n':
                if repeat == 1:
                    continue
                lista.append(" ")
                repeat = 1
            else:
                repeat = 0
                lista.append(o)
        lista = ''.join(map(str, lista))
        final_lista.append(lista)
    return final_lista


def select_text(text):
    #This function is a filter
    #It will return only the texts that contain the Keywords we are looking for
    #If not, it will force the program to go to the next article
    keywords = ["ministro", "ministério", "ministerio", "ministra", "itamaraty", "mec"]
    for i in [paragraph.lower() for paragraph in text]:
        for o in keywords:
            if o in i:
                return text        
    return False


def select_sentiment(text, f):
    #This function will ask you the sentiment of the text and each of its paragraphs
    #Later it will add all this information to an Excel spreadsheet
    origem = []
    texto_pd = []
    sentimento = []
    text_sent = []
    nome_jornal = []
    data = []
    print(text)
    full_text_sent = input("Qual o sentimento geral desse texto? \n")
    if full_text_sent == "ignore":
        return False
    for i in text:
        print(i)
        sentiment = input("Qual o sentimento desse trecho? \n")
        nome_jornal.append(f[-20:-13])
        data.append(f[-13:-4])
        origem.append(f[:-4])
        texto_pd.append(i)
        sentimento.append(sentiment)
        text_sent.append(full_text_sent)
        
    df_articles = pd.DataFrame(columns=['Origem', 'Data', 'Nome do Arquivo', 'Texto', 'Sentimento', 'Sentimento Geral'])
    add_lists = {'Origem': nome_jornal, 'Data': data, 'Nome do Arquivo': origem, 'Texto': texto_pd, 'Sentimento': sentimento, 'Sentimento Geral': text_sent}
    articles_organized = df_articles.append(pd.DataFrame(add_lists))
    read_df = pd.read_excel('Planilhas/articles sentiment.xlsx', engine='openpyxl')
    articles_sent = read_df.append(pd.DataFrame(articles_organized))
    articles_sent.to_excel('Planilhas/articles sentiment.xlsx', encoding='utf-8', index=False)
    return True

if __name__ == '__main__':

    #Here we are calling all these functions
    path = "Database Ed/"    
    files = os.listdir('Database Ed')
    where_stoped = pd.read_excel('Planilhas/articles sentiment.xlsx', engine='openpyxl')
    try:
        where_stoped = where_stoped['Nome do Arquivo'].iloc[-1]
    except Exception:
        print("Your spreadsheet is empty, let's continue")
        restart_where_stoped = False
        where_stoped = "0"
    
    for f in files:
        if f[:-4] != where_stoped and restart_where_stoped is True:
            continue
        elif f[:-4] == where_stoped and restart_where_stoped is True:
            restart_where_stoped = False
            continue
        else:
            pass
        
        file_path = (os.path.join(path, f))
        start = time.time()
        text = read_text(file_path)
        end = time.time()
        print(end - start)
        text = clean_text(text)
        text = select_text(text)
        if text:
            str_text = lista = ' '.join(map(str, text))
            with open("txt banco/{}.txt".format(f[:-4]), "w+", encoding='utf-8') as output:
                output.write(str_text)
         else:
            continue
            
        if only_clean is False:
            approved = select_sentiment(text, f)
            if not approved:
                os.remove("txt banco/{}.txt".format(f[:-4]))   

