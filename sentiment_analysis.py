import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import random
import math

signs_to_delet = [' ', ',', '.', ':', ';', '—', '(', ')', 'r']
stop_words = stopwords.words("portuguese")
for sign in signs_to_delet:
    stop_words.append(sign)
df_sentiments = pd.read_excel('Planilhas/articles sentiment.xlsx', engine='openpyxl')
pre_text_pos = [word_tokenize(f.lower()) for f in df_sentiments[(df_sentiments['Sentimento']==1)]['Texto'].tolist()]
pre_text_neg = [word_tokenize(f.lower())  for f in df_sentiments[(df_sentiments['Sentimento']==-1)]['Texto'].tolist()]
    
text_pos = []
for word_lista in pre_text_pos:
    words = []
    for word in word_lista:
        if word not in stop_words:
            words.append(word)
    text_pos.append(words)

text_neg = []
for word_lista in pre_text_neg:
    words = []
    for word in word_lista:
        if word not in stop_words:
            words.append(word)
    text_neg.append(words)

documents = ([(name, 'pos') for name in text_pos] +
             [(name, 'neg') for name in text_neg])

random.shuffle(documents)

all_words = []
for text in text_pos:
    for word in text:
        all_words.append(word)
for text in text_neg:
    for word in text:
        all_words.append(word)

all_words = nltk.FreqDist(all_words)
word_features = list(all_words.keys())[:2000]

def find_features(documents):
    #If the word is in the list of words we considerer to be relevant to the analysis, then it will be add them to the classifier as True, else, False.
    words = set(documents)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

#Creating a features set with True or False. If it is contained in the features, then the word will be True, if not, then False. 
#This will give enough info to the algorythm to create a classifier.
featuresets = [(find_features(rev), category) for (rev, category) in documents] 

#Separating a training set and a testing set. Since it is already shuffled, we are just dividing it in two.
separation = math.floor(len(featuresets)/2)
training_set = featuresets[:separation]
testing_set = featuresets[separation:]

#Naive Bayes: posterior = prior occurences * likelihood / evidence 
classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Naive Bayes Algo accuracy percent:", (nltk.classify.accuracy(classifier, testing_set)*100))
classifier.show_most_informative_features(15)

def form_sent(sent):
    return {word: True for word in nltk.word_tokenize(sent)}

text = form_sent("Quando estiver concluído, o Rodoanel terá 174 quilômetros de extensão, interligando dez rodovias. O governador Alckmin tem demonstrado que é possível construir e preservar o meio ambiente, como foi feito, por exemplo, na nova pista da Imigrantes. Processos técnicos muito modernos impediram que as águas drenadas durante as escavações contaminas sem os córregos da região.")
a = classifier.classify(text)
print(a)
