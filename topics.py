import numpy as np

import sys


import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


import gensim
import gensim.models.ldamodel as glda
from gensim import corpora

from gensim.models import CoherenceModel
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)


import pyLDAvis
import pyLDAvis.gensim 


import string




def clean(doc):
    
    removed_punctuation = ''.join( ch for w in doc for ch in w if ch not in exclude_punctuation)
    normalized = " ".join(lemma.lemmatize(word) for word in removed_punctuation.split())
    stemed = " ".join(stemmer.stem(word) for word in normalized.split()) 
    removed_digits = " ".join(([(''.join([ch for ch in w if not ch.isdigit()])) for w in stemed.split() if not w.isdigit() ]))
    remove_words = " ".join([w for w in removed_digits.split() if len(w) > 3 ])
    result = " ".join([w for w in remove_words.lower().split() if w not in stop])

    return result


file =  'admissionLife.txt'

stop = set(stopwords.words('english'))
[stop.add(line.replace('\n', '')) for line in open('StopWords.txt').readlines()]
print(stop)

exclude_punctuation = set(string.punctuation)

lemma = WordNetLemmatizer()

stemmer = nltk.stem.PorterStemmer()

with open(file,'r') as fr:
  list_text = [clean(line)+'\n' for line in fr]
fr.close()




flog = open('log_life_11k', 'w')

print('Leitura Arquivo: ',file)
flog.write('Leitura Arquivo' + file)
docs = []

for l in list_text:
    docs.append(l.replace('\n','').split())   


print('Carregado {} palavras'.format(len(docs))) 
flog.write('Carregado {} palavras'.format(len(docs)))

dictionaryDocs = corpora.Dictionary(docs)
noBelow = round((len(docs) * 0.10))
dictionaryDocs.filter_extremes(no_below=noBelow, no_above=0.8, keep_n=10000)


doc_term_matrix = [dictionaryDocs.doc2bow(doc) for doc in docs]

SOME_FIXED_SEED = 100

np.random.seed(SOME_FIXED_SEED)

ldamodel = gensim.models.LdaMulticore(corpus=doc_term_matrix,
                                        id2word=dictionaryDocs,
										                    workers = 4,
                                        num_topics=11, 
                                        random_state=SOME_FIXED_SEED,
                                        iterations = 1000,
                                        passes=50,
                                        alpha=0.01)





for idx, topic in ldamodel.print_topics(-1):
  print("Topic: {} \nWords: {}".format(str(idx), [topic]))
  flog.write("Topic: {} \nWords: {}".format(str(idx), [topic]))
  print("\n")
  flog.write("\n")


coherencemodel = CoherenceModel(model=ldamodel, texts=docs, dictionary=dictionaryDocs, coherence='c_v')
print('\nCoherence Score: ', coherencemodel.get_coherence())
flog.write("\nCoherence Score: {}".format(coherencemodel.get_coherence()))



from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS

import matplotlib.colors as mcolors

cols = [color for name, color in mcolors.XKCD_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'

cloud = WordCloud(
                  background_color='white',
                  width=2500,
                  height=1800,
                  max_words=10,
                  colormap='tab10',
                  color_func=lambda *args, **kwargs: cols[i],
                  prefer_horizontal=1.0)

topics = ldamodel.show_topics(num_topics=11,num_words=10, formatted=False)

fig, axes = plt.subplots(1, 11, figsize=(100,100), sharex=True, sharey=True)

for i, ax in enumerate(axes.flatten()):
    fig.add_subplot(ax)
    topic_words = dict(topics[i][1])
    cloud.generate_from_frequencies(topic_words, max_font_size=300)
    plt.gca().imshow(cloud)
    plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
    plt.gca().axis('off')


plt.subplots_adjust(wspace=0, hspace=0)
plt.axis('off')
plt.margins(x=0, y=0)
plt.tight_layout()
plt.savefig('words.pdf')

pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(ldamodel, doc_term_matrix, dictionaryDocs)
pyLDAvis.save_html(vis,'vis.html')


from gensim.test.utils import datapath
temp_file = datapath("model")
ldamodel.save(temp_file)

flog.close()
