# -*- encoding: utf8 -*-
# author: chenbjin
# time: 2018/03/18 11:01:36

import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import load_model

from utils import load_data, split_data
from utils import convert_to_keras_target, convert_to_char_label
from common import INPUT_SHAPE, BATCH_SIZE, EPOCHS
from architecture import convnet, multi_convnet

def train(x_train, y_train, x_test, y_test, default_model='multi_convnet', num_class=4):
    """Train model"""
    if default_model == 'multi_convnet':
        model = multi_convnet(INPUT_SHAPE, num_class)
    else:
        model = convnet(INPUT_SHAPE, num_class)
    
    # trainning setting
    save_path = 'output/'  + 'weights.{epoch:02d}-{val_loss:.2f}.h5'
    check_pointer = ModelCheckpoint(save_path, save_best_only=True)
    earlystop = EarlyStopping(monitor='val_loss', patience=2, verbose=1, mode='auto')
    callback_list = [earlystop, check_pointer]

    # trainning
    model.fit(x_train, y_train,
             batch_size=BATCH_SIZE,
             epochs=EPOCHS,
             verbose=1,
             validation_data=(x_test, y_test),
             callbacks=callback_list)
    model.save('my_model.h5')
    return model

def pred(model, x_pred, labels=None):
    """Predict and test"""
    y_pred = model.predict(x_pred, batch_size=BATCH_SIZE)
    y_pred_labels = convert_to_char_label(y_pred) 
    if labels:
        nb_labels = len(labels)
        nb_correct = sum(y_pred_labels[i] == labels[i] for i in range(nb_labels))
        nb_ign_correct = sum(y_pred_labels[i].lower() == labels[i].lower() for i in range(nb_labels))
        print "Acc: %f(%d/%d)"%(nb_correct*1.0/nb_labels, nb_correct, nb_labels)
        print "Ignore case Acc: %f(%d/%d)"%(nb_ign_correct*1.0/nb_labels, nb_ign_correct, nb_labels)
        return None
    return y_pred_labels

if __name__ == '__main__':
    [data, labels] = load_data()
    [x_train, y_train, x_test, y_test] = split_data(data, labels)
    val_labels = y_test
    
    x_train = np.array(x_train)
    x_train = 255 - x_train
    x_train /= 255
    x_test = np.array(x_test)
    x_test = 255 - x_test
    x_test /= 255
    #print x_train.shape
    
    y_train = convert_to_keras_target(y_train)
    y_test = convert_to_keras_target(y_test)
    #y_train = np.array(y_train)
    #y_test = np.array(y_test)
    print len(y_train) 
    print y_train[0].shape
    print len(y_test) 
    print y_test[0].shape
    
    model = train(x_train, y_train, x_test, y_test)
    #model = load_model('my_model.h5')
    pred(model, x_test, val_labels)