import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

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

label_dict = dict(zip(list(label_encoder.classes_), \
                      label_encoder.transform(label_encoder.classes_)))
