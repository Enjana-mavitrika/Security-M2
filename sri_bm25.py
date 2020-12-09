import re # use regex
#import os
import nltk
import json
import time
import math
nltk.download('punkt')
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
englishStemmer=SnowballStemmer("english", ignore_stopwords=True)
from nltk.corpus import wordnet 

tokenizer = RegexpTokenizer(r'\w+')

start_time = time.time()

N = 0
K = 1500
groupe_name = "FaresIbrahimaSolofo"
w_q = {}
scores = {}

querys = {
    2009011 : ["olive", "oil", "health", "benefit"],
    2009036 : ["notting", "hill", "film", "actors"],
    2009067 : ["probabilistic", "models", "in", "information", "retrieval"],
    2009073 : ["web", "link", "network", "analysis"],
    2009074 : ["web", "ranking", "scoring", "algorithm"],
    2009078 : ["supervised", "machine", "learning", "algorithm"],
    2009085 : ["operating", "system", "mutual", "exclusion"] 
}


# lire le fichier contenant la collection 
file = open('Text_Only_Ascii_Coll_MWI_NoSem', 'r')
lines = file.readlines()
docCount = 0
# on va parser les documents par numéro
documents = {}
numDoc = 0
tf = {}
df = {}

print("traitement en cours...")
for line in lines :
    if (re.search("<doc><docno>", line)) : # on retrouve un nouveau document
        N += 1
        numDoc = re.search("[0-9]+", line).group()
        documents[numDoc] = 0.0
        #print("process {}".format(numDoc))
    else :
        line_lower=line.lower()
        #print(line_lower)
        tokens = tokenizer.tokenize(line_lower)
        #print(tokens)
        #print("\n\n")
        for term in tokens :
            documents[numDoc] += 1.0
            if term not in stop_words and not term.isnumeric() and len(term) > 2 :
                stem_term = englishStemmer.stem(term)
                if (numDoc, stem_term) in tf.keys() :
                    tf[numDoc, stem_term] += 1.0
                else :
                    tf[numDoc, stem_term] = 1.0
                    if stem_term in df.keys() :
                        df[stem_term] += 1.0
                    else :
                        df[stem_term] = 1.0

sum_size = 0
for id in documents.keys() :
    sum_size += documents[id]

avgdl = sum_size/N
print("avdl = ", avgdl)
k1 = 2.0
b = 0.75

print("df[inform] = ", df["inform"])

for query_id in querys.keys() :
    for query in querys[query_id] :
        term = englishStemmer.stem(query)
        print("query : ", term)
        if term in df.keys() :
            #w_q[term] = math.log(N/df[term])
            for doc in documents.keys() :
                #print("doc = ", doc)
                if (doc, term) in tf.keys() :
                    qi = (N - df[term] + 0.5) / (df[term] + 0.5)
                    idf = math.log(qi)
                    w = idf * ((tf[doc, term] * (k1 + 1)) / (tf[doc, term] + k1 * (1 - b + b * (documents[doc]/avgdl))))
                    if doc in scores.keys() :
                        scores[doc] += w  
                    else :
                        scores[doc] =  w
    
    for doc in documents.keys() :
        if doc in scores.keys() :
            scores[doc] /= documents[doc]
        else :
            scores[doc] = 0.0
    #print(scores)
    run = ""
    last_not_null_max_score = 0.001500
    for i in range(K) :
        max_key = max(scores, key=scores.get)
        score = scores[max_key]
        if score == 0.0 :
            score = last_not_null_max_score - 0.00000001
        last_not_null_max_score = score
        run += "{} Q0 {} {} {:.8f} {} /article[1]\n".format(query_id, max_key, i+1, score, groupe_name)
        scores[max_key] = -1

    with open('run/FaresIbrahimaSolofo_03_07_bm25_steming_k2.0b0.75.txt', 'a') as run_file :
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))