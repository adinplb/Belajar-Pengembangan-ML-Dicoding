# -*- coding: utf-8 -*-
"""Proyek Pertama NLP Dicoding

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16vw2oBF3ogASnq_aowkGCiIwX_fNCyaw
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import re
import nltk

from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from google.colab import drive
drive.mount ('/content/drive')

df = pd.read_csv('/content/drive/MyDrive/pengembangan-ML-dicoding/alldata_1_for_kaggle.csv', header = None, encoding='latin1') #read csv file

df.head() #display top rows

df = df[[1,2]]
df.columns=['labels','text']

df.tail() #display bottom rows

df.dtypes #display data types

df.describe() #summary statistics

df.info() #display index, columns and data

len(df)

df['targets'] = df['labels'].astype('category').cat.codes

df

'''
category = pd.get_dummies(df.labels)
df_cleaned = pd.concat([df, category], axis=1)
df_cleaned = df_cleaned.drop(columns='labels')
df_cleaned
'''

#df = df.sample(4000)

#df

'''
df_removed = df_cleaned.drop(columns=['0'])
df_removed2 = df_removed.drop(df_removed.index[0])
df_removed2
'''

# menghilangkan tanda baca & angka pada coloumn content
def remove_punctuations_numbers(inputs):
    return re.sub(r'[^a-zA-Z]', ' ', inputs)


df['text'] = df['text'] .apply(remove_punctuations_numbers)

def hapus_ulasan_special(text):
    # hapus tab, new line, ans back slice
    text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
    # hapus non ASCII (emoticon, chinese word, .etc)
    text = text.encode('ascii', 'replace').decode('ascii')
    # hapus mention @
    text = re.sub(r"[@][\w_-]+","", text)
    # hapus link, hashtag
    text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
    # hapus incomplete URL
    return text.replace("http://", " ").replace("https://", " ")

df['text'] = df['text'].apply(hapus_ulasan_special)

#hapus whitespace leading & trailing
def hapus_whitespace_LT(text):
    return text.strip()

df_removed2['text'] = df_removed2['text'].apply(hapus_whitespace_LT)

#hapus multiple whitespace into single whitespace
def hapus_whitespace_multiple(text):
    return re.sub('\s+',' ',text)

df['text'] = df['text'].apply(hapus_whitespace_multiple)

# hapus single char
def hapus_singl_char(text):
    return re.sub(r"\b[a-zA-Z]\b", "", text)

df['text'] = df['text'].apply(hapus_singl_char)

#hapus pengulangan dalam kata
def replaceThreeOrMore (text):
    #Pattern to look for three or more repetitions of any character, including newlines(contoh goool -> gool)
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", text)

df['text'] = df['text'].apply(replaceThreeOrMore)

#Case Folding
df['text'] = df['text'] .str.lower()

# mengecek data yang telah di prepocessing
df

df2 = df.drop(df.index[0])

df2

#bagi dataset menjadi train dan label
x = df2['text'].values
y = df2['targets'].values

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

'''
from tensorflow.keras.utils import to_categorical

y_train = to_categorical(y_train, 3)
y_test = to_categorical(y_test, 3)#
'''

tokenizer = Tokenizer(num_words=5000, oov_token='x')
tokenizer.fit_on_texts(x_train)
tokenizer.fit_on_texts(x_test)

sekuens_train = tokenizer.texts_to_sequences(x_train)
sekuens_test = tokenizer.texts_to_sequences(x_test)

padded_train = pad_sequences(sekuens_train)
padded_test = pad_sequences(sekuens_test)

'''
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax')
])
model.compile(loss='categorical_crossentropy' ,optimizer='adam',metrics=['accuracy'])
'''


#buat model arsitektur dan compile
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

model = Sequential([
  Embedding(input_dim = 5000, output_dim = 16),
  LSTM(64),
  Dense(128, activation = 'relu'),
  Dense(64, activation = 'relu'),
  Dense(9, activation = 'softmax')
])

model.compile(
  loss = 'sparse_categorical_crossentropy',
  optimizer = 'adam',
  metrics = ['accuracy']
)

#buat callbacks untuk persingkat waktu pelatihan model
class myCallback(tf.keras.callbacks.Callback) :
  def end_epoch(self, epoch, logs={}):
    if(logs.get('accuracy')>0.75):
      i = logs.get('accuracy')
      self.model.stop_training =True
callbacks = myCallback()

history = model.fit(
  padded_train, y_train, epochs = 30,  callbacks=[callbacks],
  validation_data = (padded_test, y_test), verbose = 2)

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

