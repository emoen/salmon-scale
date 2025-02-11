import numpy as np
import pandas as pd
import os
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.utils import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import scipy

import tensorflow as tf

from keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping
from keras.preprocessing.image import img_to_array, load_img, ImageDataGenerator
from keras.optimizers import SGD
from keras.applications.imagenet_utils import decode_predictions
from keras.layers import Activation, Dense, GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.models import Model
from keras.utils import to_categorical
from keras import optimizers, layers
from keras import backend as K

from train_util import read_images, load_xy, get_checkpoint_tensorboard, create_model_grayscale, get_fresh_weights, base_output, dense1_linear_output, train_validate_test_split, dense_classification_softmax

#from efficientnet import EfficientNetB4
import efficientnet.keras as efn

new_shape = (380, 380, 3)
IMG_SHAPE = (380, 380)
tensorboard_path = './tensorboard_farmed_uten_ukjent_patience_20'
checkpoint_path = './checkpoints_farmed_uten_ukjent_patience_20/salmon_scale_efficientnetB4.{epoch:03d}-{val_loss:.2f}.hdf5'
FARMED_CLASS = 'vill'
SPAWN_CLASS = 'gytarar'

def do_train():
    global new_shape, tensorboard_path, checkpoint_path, to_predict, dataset_size_selected

    os.environ["CUDA_VISIBLE_DEVICES"]="0"
    age = []
    a_batch_size = 8

    rb_imgs, all_sea_age, all_smolt_age, all_farmed_class, all_spawn_class, all_filenames = load_xy()

    uten_ukjent = all_farmed_class.count('vill') + all_farmed_class.count('oppdrett')
    rb_imgs2 = np.empty(shape=(uten_ukjent,)+new_shape)
    print("count vill:"+str(all_farmed_class.count('vill')))
    print("count oppdrett:"+str(all_farmed_class.count('oppdrett')))
    print("count uten_ukjent:"+str(uten_ukjent))     
            
    all_farmed_class2 = []
    found_count = 0
    count_vill_added = 0
    all_filenames2 = []
    for i in range(0, len(all_farmed_class)):
        if all_farmed_class[i] != 'ukjent':
            all_filenames2.append(all_filenames[i])
            if all_farmed_class[i] == 'vill' and count_vill_added < uten_ukjent:
                rb_imgs2[found_count] = rb_imgs[i]
                all_farmed_class2.append(all_farmed_class[i])
                found_count += 1
                count_vill_added += 1
            if all_farmed_class[i] == 'oppdrett':
                rb_imgs2[found_count] = rb_imgs[i]
                all_farmed_class2.append(all_farmed_class[i])
                found_count += 1

    print("all_farmed_class:"+str(all_farmed_class[0:10]))
    print("all_farmed_class2:"+str(all_farmed_class2[0:10]))
    print("found_count after add:"+str(found_count))
    print("count_vill_added:"+str(count_vill_added))

    rb_imgs = rb_imgs2
    all_farmed_class = all_farmed_class2
    all_y_true = all_farmed_class
    print("count uten_ukjent:"+str(uten_ukjent)+" all_farmed_class:"+str(len(all_farmed_class)))

    #if to_classify == to_classify_spawning    
    #    all_y_true = all_spawn_class

    label_encoder = preprocessing.LabelEncoder()
    integer_encoded = label_encoder.fit_transform( all_y_true )
    encoded = to_categorical(integer_encoded )
    age = encoded
    
    print("age encoded:**************************")
    print(str(age[0:5]))
    print(str(set(all_y_true)))
    print("vill/ikke_gytar:"+str(all_y_true.count('vill'))+"," +str(all_y_true.count('oppdrett')))
    #print("oppdrett/gytar:"+str(all_y_true.count(to_classify_smallest)))
    print("len(all_y_true):"+str(len(all_y_true)))

early_stopper = EarlyStopping(patience=20)
train_datagen = ImageDataGenerator(
    zca_whitening=True,
    width_shift_range=5,
    height_shift_range=5, 
    zoom_range=0.,
    rotation_range=360,
    horizontal_flip=False,
    vertical_flip=True,
    rescale=1./255)
    
train_idx, val_idx, test_idx = train_validate_test_split( range(0, len(rb_imgs)) )
train_rb_imgs = np.empty(shape=(len(train_idx),)+new_shape)
train_age = []
for i in range(0, len(train_idx)):
    train_rb_imgs[i] = rb_imgs[train_idx[i]]
    train_age.append(age[train_idx[i]])

val_rb_imgs = np.empty(shape=(len(val_idx),)+new_shape)
val_age = []
for i in range(0, len(val_idx)):
    val_rb_imgs[i] = rb_imgs[val_idx[i]]
    val_age.append(age[val_idx[i]])

test_rb_imgs = np.empty(shape=(len(test_idx),)+new_shape)
test_age = []
test_age_names = []
for i in range(0, len(test_idx)):
    test_rb_imgs[i] = rb_imgs[test_idx[i]]
    test_age.append(age[test_idx[i]])
    test_age_names.append(all_filenames2[test_idx[i]])

train_age = np.vstack(train_age)
val_age = np.vstack(val_age)
test_age = np.vstack(test_age)

val_rb_imgs = np.multiply(val_rb_imgs, 1./255)
test_rb_imgs = np.multiply(test_rb_imgs, 1./255)

    train_generator = train_datagen.flow(train_rb_imgs, train_age, batch_size= a_batch_size)

    rgb_efficientNetB4 = efn.EfficientNetB4(include_top=False, weights='imagenet', input_shape=new_shape, classes=2)
    z = dense_classification_softmax( rgb_efficientNetB4 )
    scales = Model(inputs=rgb_efficientNetB4.input, outputs=z)

    learning_rate=0.00007
    adam = optimizers.Adam(lr=learning_rate)

    for layer in scales.layers:
        layer.trainable = True
            
    scales.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy']) #,'mse', 'mape'] )
    tensorboard, checkpointer = get_checkpoint_tensorboard(tensorboard_path, checkpoint_path)

    classWeight = compute_class_weight('balanced', np.unique(all_y_true), all_y_true)
    classWeight = dict(enumerate(classWeight))
    print("classWeight:"+str(classWeight))

    history_callback = scales.fit_generator(train_generator,
        steps_per_epoch=1600,
        epochs=150,
        callbacks=[early_stopper, tensorboard, checkpointer],
        validation_data=(val_rb_imgs, val_age),
        class_weight=classWeight)

    test_metrics = scales.evaluate(x=test_rb_imgs, y=test_age)
    print("test metric:"+str(scales.metrics_names))
    print("test metrics:"+str(test_metrics))

    print("precision, recall, f1")
    y_pred_test = scales.predict(test_rb_imgs, verbose=1)
    y_pred_test_bool = np.argmax(y_pred_test, axis=1)
    y_true_bool = np.argmax(test_age, axis=1)
    df_y_hat = pd.DataFrame(columns=['filename','y_hat', 'y'])
    all_names = [str(d)[51:] for d in test_age_names]
    df_y_hat['filename'] = all_names
    df_y_hat['y_hat'] = y_pred_test_bool
    df_y_hat['y'] = y_true_bool
    df_y_hat.to_csv('test_set_oppdrett.csv', sep=' ', index=False)
    #np.argmax inverse of to_categorical
    argmax_test = np.argmax(test_age, axis=1)
    unique, counts = np.unique(argmax_test, return_counts=True)
    print("test ocurrence of each class:"+str(dict(zip(unique, counts))))

    print("cslassification_report")
    print(classification_report(y_true_bool, y_pred_test_bool))
    print("confusion matrix")
    print(str(confusion_matrix(y_true_bool, y_pred_test_bool)))

if __name__ == '__main__':
    do_train()
