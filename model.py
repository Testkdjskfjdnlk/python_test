import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#matplotlib inline

from sklearn import preprocessing
from sklearn.externals import joblib

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.layers import Dense, Input, Flatten
from keras.layers import Reshape, Dropout, Concatenate
from keras.layers import Conv2D, MaxPool2D, Embedding
from keras.models import Model

BASE_DIR = '/Users/charlotte/Documents/study/aussem4/comp9900/'
train_text_file = 'train_text.txt'
train_label_file = 'train_label.txt'
MAX_SEQUENCE_LENGTH = 50
MAX_NB_WORDS = 20000
EMBEDDING_DIM = 100
VALIDATION_SPLIT = 0.10


with open(train_text_file,'r') as f:
    train_text = f.read().splitlines()
with open(train_label_file,'r') as f:
    train_label = f.read().splitlines()
    
#label encoding
label_encoder = preprocessing.LabelEncoder()
label_encoder.fit(train_label)

#save the labels encoder
joblib.dump(label_encoder, 'label_encoder.pkl')

train_label = label_encoder.transform(train_label)

label_dict = dict(zip(list(label_encoder.classes_), label_encoder.transform(label_encoder.classes_)))

#Tokenizing text and creating word index
tokenizer = Tokenizer(num_words = MAX_NB_WORDS)
tokenizer.fit_on_texts(train_text)
sequences = tokenizer.texts_to_sequences(train_text)

word_index = tokenizer.word_index

data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

train_label = to_categorical(np.asarray(train_label))

#Creating embedding matrix from Glove vectors
embeddings_index = {}
with open(BASE_DIR + '/glove.6B' + '/glove.6B.100d.txt', encoding = 'utf-8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype = 'float32')
        embeddings_index[word] = coefs
 

num_words = min(MAX_NB_WORDS, len(word_index))
embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        #word not founf in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector

filter_sizes = [2,3,5]
num_filters = 512
drop = 0.5

inputs = Input(shape = (MAX_SEQUENCE_LENGTH,), dtype = 'int32')
embedding = Embedding(input_dim = len(word_index) + 1, output_dim = EMBEDDING_DIM, weights = [embedding_matrix],\
                     input_length = MAX_SEQUENCE_LENGTH, trainable = False)(inputs)
reshape = Reshape((MAX_SEQUENCE_LENGTH, EMBEDDING_DIM,1))(embedding)

conv_0 = Conv2D(num_filters, kernel_size = (filter_sizes[0], EMBEDDING_DIM), padding = 'valid', kernel_initializer = 'normal',\
               activation = 'relu')(reshape)
conv_1 = Conv2D(num_filters, kernel_size = (filter_sizes[1], EMBEDDING_DIM), padding = 'valid', kernel_initializer = 'normal',\
               activation = 'relu')(reshape)
conv_2 = Conv2D(num_filters, kernel_size = (filter_sizes[2], EMBEDDING_DIM), padding = 'valid', kernel_initializer = 'normal',\
               activation = 'relu')(reshape)

maxpool_0 = MaxPool2D(pool_size = (MAX_SEQUENCE_LENGTH - filter_sizes[0] + 1, 1), strides = (1,1), padding = 'valid')(conv_0)
maxpool_1 = MaxPool2D(pool_size = (MAX_SEQUENCE_LENGTH - filter_sizes[1] + 1, 1), strides = (1,1), padding = 'valid')(conv_1)
maxpool_2 = MaxPool2D(pool_size = (MAX_SEQUENCE_LENGTH - filter_sizes[2] + 1, 1), strides = (1,1), padding = 'valid')(conv_2)

concatenated_tensor = Concatenate(axis = 1)([maxpool_0, maxpool_1, maxpool_2])
flatten = Flatten()(concatenated_tensor)
dropout = Dropout(drop)(flatten)
preds = Dense(len(label_dict), activation = 'softmax')(dropout)

model = Model(inputs = inputs, outputs = preds)
model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['acc'])

history = model.fit(data, train_label, batch_size = 32, epochs = 10, validation_data = (data, train_label))

# testing model
test_texts = ['hello',\
              'Who is teaching COMP9321 this semester?',\
              'What courses should I take as a data science student',\
              'What courses should I take?',\
              'What courses should I take to meet the graduate requirements?',\
              'Will these courses you recommended cause time clash?',\
              'Bye, thank you for you help'
             ]
test_sequences = tokenizer.texts_to_sequences(test_texts)
test_input = pad_sequences(test_sequences, maxlen = MAX_SEQUENCE_LENGTH)

test_predictions_probas = model.predict(test_input)
test_predictions = test_predictions_probas.argmax(axis=-1)

[[k for k,v in label_dict.items()if v == i ]for i in test_predictions]
