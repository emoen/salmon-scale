import numpy as np
import pandas as pd
import os
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.utils import compute_class_weight
from sklearn.metrics import classification_report
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

from clean_y_true import read_and_clean_farmed_salmon_csv_files, read_and_clean_spawners_csv_files

from efficientnet import EfficientNetB4


new_shape = (380, 380, 3)
IMG_SHAPE = (380, 380)
base_dir = '/gpfs/gpfs0/deep/data/salmon-scales/dataset_5_param'
id_column = 'ID nr.'
tensorboard_path = './tensorboard_missing_loss'
checkpoint_path = './checkpoints_missing_loss2/salmon_scale_inception.{epoch:03d}-{val_loss:.2f}.hdf5'
age = []
dataset_size_oppdrett = 9073

def read_images(pandas_df, rb_imgs, array_pointer, directory_with_images, to_classify):
    global base_dir, id_column

    df_age = list()
    found_count=0
    dir_path = os.path.join(base_dir, directory_with_images)
    print("path:"+dir_path+ " first file:"+str(pandas_df[id_column].values[0]))
    for i in range(0, len(pandas_df)):
        image_name = pandas_df[id_column].values[i]+'.jpg'
        path = os.path.join(dir_path, image_name )
        my_file = Path(path)
        if not my_file.is_file():
            path = os.path.join(dir_path, image_name.lower() )
            my_file = Path(path)
        if my_file.is_file():
            pil_img = load_img(path, target_size=IMG_SHAPE, grayscale=False)
            array_img = img_to_array(pil_img, data_format='channels_last')
            rb_imgs[array_pointer+found_count] = array_img
            df_age.append( pandas_df[to_classify].values[i] ) #gytarar
            found_count += 1
        ##else:
            #print("image not found:"+path)

    end_of_array = array_pointer + found_count
    return end_of_array, rb_imgs, df_age

def do_train():
    global new_shape, age, tensorboard_path, checkpoint_path, to_predict, dataset_size_selected

    os.environ["CUDA_VISIBLE_DEVICES"]="0"
    to_classify_spawning = 'gytarar'
    to_classify_wild = 'vill'
    to_classify_spawning_larges_class=False
    to_classify_spawning_smallest_class=True
    to_classify_wild_largest_class='vill'
    to_classify_wild_smallest_class='oppdrett'
    to_classify = to_classify_spawning
    to_classify_largest = to_classify_wild_largest_class
    to_classify_smallest = to_classify_wild_smallest_class
    if to_classify == to_classify_spawning:
        to_classify_largest = to_classify_spawning_larges_class
        to_classify_smallest = to_classify_spawning_smallest_class

    a_batch_size = 12
    cumulativ_add_count = 0

    rb_imgs = np.empty(shape=(dataset_size_oppdrett,)+new_shape)
    d2015, d2016, d2017, d2018, d2016rb, d2017rb = read_and_clean_farmed_salmon_csv_files( base_dir )
    if to_classify == to_classify_spawning:
        d2015, d2016, d2017, d2018, d2016rb, d2017rb = read_and_clean_spawners_csv_files( base_dir )

    cumulativ_add_count, rb_imgs, d15_age = read_images(d2015, rb_imgs, cumulativ_add_count, 'hi2015_in_excel', to_classify)
    print("cumulativ_add_count_15: "+str(cumulativ_add_count))
    cumulativ_add_count, rb_imgs, d16_age = read_images(d2016, rb_imgs, cumulativ_add_count, 'hi2016_in_excel', to_classify)
    print("cumulativ_add_count_16: "+str(cumulativ_add_count))
    cumulativ_add_count, rb_imgs, d17_age = read_images(d2017, rb_imgs, cumulativ_add_count, 'hi2017_in_excel', to_classify)
    print("cumulativ_add_count_17 :"+str(cumulativ_add_count))
    cumulativ_add_count, rb_imgs, d18_age = read_images(d2018, rb_imgs, cumulativ_add_count, 'hi2018_in_excel', to_classify)
    print("cumulativ_add_count_18 :"+str(cumulativ_add_count))
    cumulativ_add_count, rb_imgs, d16rb_age = read_images(d2016rb, rb_imgs, cumulativ_add_count, 'rb2016', to_classify)
    print("cumulativ_add_count_16rb: "+str(cumulativ_add_count))
    cumulativ_add_count, rb_imgs, d17rb_age = read_images(d2017rb, rb_imgs, cumulativ_add_count, 'rb2017', to_classify)
    print("cumulativ_add_count_17rb: "+str(cumulativ_add_count))

    merged_age = d15_age + d16_age + d17_age + d18_age + d16rb_age + d17rb_age

    if to_classify == to_classify_wild:
        uten_ukjent = merged_age.count('vill') + merged_age.count('oppdrett')
        print("count vill:"+str(merged_age.count('vill')))
        print("count oppdrett:"+str(merged_age.count('oppdrett')))
        print("count uten_ukjent:"+str(uten_ukjent))

        uten_ukjent = merged_age.count('oppdrett') * 2
        rb_imgs2 = np.empty(shape=(uten_ukjent,)+new_shape)
        merged_age2 = []
        found_count = 0
        count_vill_added = 0
        for i in range(0, len(merged_age)):
            if merged_age[i] != 'ukjent':
                if merged_age[i] == 'vill' and count_vill_added < merged_age.count('oppdrett'):
                    rb_imgs2[found_count] = rb_imgs[i]
                    merged_age2.append(merged_age[i])
                    found_count += 1
                    count_vill_added += 1
                if merged_age[i] == 'oppdrett':
                    rb_imgs2[found_count] = rb_imgs[i]
                    merged_age2.append(merged_age[i])
                    found_count += 1

        print("merged_age:"+str(merged_age[0:10]))
        print("merged_age:2"+str(merged_age2[0:10]))
        print("found_count after add:"+str(found_count))
        print("count_vill_added:"+str(count_vill_added))

        rb_imgs = rb_imgs2
        merged_age = merged_age2
        print("count uten_ukjent:"+str(uten_ukjent)+" merged_age:"+str(len(merged_age)))

    if to_classify == to_classify_spawning:
        uten_ukjent = merged_age.count(True) + merged_age.count(False)
        print("true count:"+str(merged_age.count(True)))
        print("false count:"+str(merged_age.count(False)))

        uten_ukjent = merged_age.count(True)*2
        rb_imgs2 = np.empty(shape=(uten_ukjent,)+new_shape)
        merged_age2 = []
        found_count = 0
        count_false_added = 0
        for i in range(0, len(merged_age)):
            if merged_age[i] == False and count_false_added < merged_age.count(True):
                rb_imgs2[found_count] = rb_imgs[i]
                merged_age2.append(merged_age[i])
                found_count += 1
                count_false_added += 1
            if merged_age[i] == True:
                rb_imgs2[found_count] = rb_imgs[i]
                merged_age2.append(merged_age[i])
                found_count += 1

        print("merged_age:"+str(merged_age[0:10]))
        print("merged_age:2"+str(merged_age2[0:10]))
        print("found_count after add:"+str(found_count))
        print("count_false_added:"+str(count_false_added))

        rb_imgs = rb_imgs2
        merged_age = merged_age2
        print("count uten_ukjent:"+str(uten_ukjent)+" merged_age:"+str(len(merged_age)))

    label_encoder = preprocessing.LabelEncoder()
    integer_encoded = label_encoder.fit_transform( merged_age )
    encoded = to_categorical(integer_encoded )
    age = encoded
    print("age encoded:**************************")
    print(str(age[0:5]))
    print(str(set(merged_age)))
    print("vill/ikke_gytar:"+str(merged_age.count(to_classify_largest)))
    print("oppdrett/gytar:"+str(merged_age.count(to_classify_smallest)))
    print("len(merged_age):"+str(len(merged_age)))
    print("smallest + largest:"+str(merged_age.count(to_classify_largest)+merged_age.count(to_classify_smallest)))
    early_stopper = EarlyStopping(patience=5)
    train_datagen = ImageDataGenerator(
        zca_whitening=True,
        width_shift_range=0.,
        height_shift_range=0., #20,
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
    for i in range(0, len(test_idx)):
        test_rb_imgs[i] = rb_imgs[test_idx[i]]
        test_age.append(age[test_idx[i]])

    train_age = np.vstack(train_age)
    val_age = np.vstack(val_age)
    test_age = np.vstack(test_age)

    #print("train size:"+str(len(train_age))+" smallest class:"+str(train_age.count(to_classify_smallest)))
    #print("val size:"+str(len(val_age))+" smallest class:"+str(val_age.count(to_classify_smallest)))
    #print("test size:"+str(len(test_age))+" smallest class:"+str(test_age.count(to_classify_smallest)))

    val_rb_imgs = np.multiply(val_rb_imgs, 1./255)
    test_rb_imgs = np.multiply(test_rb_imgs, 1./255)

    train_generator = train_datagen.flow(train_rb_imgs, train_age, batch_size= a_batch_size)

    #gray_model, gray_model_weights = create_model_grayscale(new_shape)
    #gray_model = get_fresh_weights( gray_model, gray_model_weights )
    rgb_efficientNetB4 = EfficientNetB4(include_top=False, weights='imagenet', input_shape=new_shape, classes=2)
    z = dense3_vill( rgb_efficientNetB4 )
    scales = Model(inputs=rgb_efficientNetB4.input, outputs=z)

    learning_rate=0.0001
    adam = optimizers.Adam(lr=learning_rate)

    for layer in scales.layers:
        layer.trainable = True
    scales.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'] )

    tensorboard, checkpointer = get_checkpoint_tensorboard(tensorboard_path, checkpoint_path)

    classWeight = compute_class_weight('balanced', np.unique(merged_age), merged_age)
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
    preds = scales.predict(test_rb_imgs)

    print("precision, recall, f1")
    y_pred_test = scales.predict(test_rb_imgs, verbose=1)
    y_pred_test_bool = np.argmax(y_pred_test, axis=1)
    y_true_bool = np.argmax(test_age, axis=1)

    print("cslassification_report")
    print(classification_report(y_true_bool, y_pred_test_bool))
    print("confusion matrix")
    print(str(confusion_matrix(y_true_bool, y_pred_test_bool)))

def get_checkpoint_tensorboard(tensorboard_path, checkpoint_path):

    tensorboard = TensorBoard(log_dir=tensorboard_path)
    checkpointer = ModelCheckpoint(
        filepath = checkpoint_path,
        verbose = 1,
        save_best_only = True,
        save_weights_only = False)
    return tensorboard, checkpointer

def create_model_grayscale(new_shape):

    model_no_sf = EfficientNetB4(include_top=False, weights='imagenet', input_shape=new_shape, classes=2)

    #inception_no_sf = InceptionV3(include_top=False, weights='imagenet', input_shape=(299, 299, 3)) #Inception V3 without applying softmax
    '''Modify architecture of the InceptionV3 for grayscale data'''
    model_no_sf_config=model_no_sf.get_config() #Copy configuration
    gray_model_config=dict(model_no_sf_config)
    gray_model_config['layers'][0]['config']['batch_input_shape']=((None,)+ new_shape) #Change input shape

    model_no_sf_weights=model_no_sf.get_weights() #Copy weights
    gray_model_weights =model_no_sf_weights.copy()
    gray_model_weights[0] = model_no_sf_weights[0][:,:,0,:].reshape([3,3,1,-1]) #Only use filter for red channel for transfer learning

    gray_model=Model.from_config(gray_model_config) #Make grayscale model

    return gray_model, gray_model_weights

def get_fresh_weights(gray_model, gray_model_weights):
    gray_model.set_weights(gray_model_weights)
    return gray_model

def base_output(gray_model):
    z = gray_model.output
    z = GlobalMaxPooling2D()(z)
    return z

def dense3_vill(gray_model):
    z = base_output(gray_model)
    z = Dense(2)(z)
    z = Activation('softmax')(z)
    return z

# Define our custom loss function
def focal_loss(y_true, y_pred):
    gamma = 2.0
    alpha = 0.25
    pt_1 = tf.where(tf.equal(y_true, 1), y_pred, tf.ones_like(y_pred))
    pt_0 = tf.where(tf.equal(y_true, 0), y_pred, tf.zeros_like(y_pred))
    return -K.sum(alpha * K.pow(1. - pt_1, gamma) * K.log(pt_1))-K.sum((1-alpha) * K.pow( pt_0, gamma) * K.log(1. - pt_0))

def matthews_correlation(y_true, y_pred):
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos

    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos

    tp = K.sum(y_pos * y_pred_pos)
    tn = K.sum(y_neg * y_pred_neg)

    fp = K.sum(y_neg * y_pred_pos)
    fn = K.sum(y_pos * y_pred_neg)

    numerator = (tp * tn - fp * fn)
    denominator = K.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    return numerator / (denominator + K.epsilon())

def train_validate_test_split(pairs, validation_set_size = 0.15, test_set_size = 0.15, a_seed = 8):
    """ split pairs into 3 set, train-, validation-, and test-set
        1 - (validation_set_size + test_set_size) = % training set size
    >>> import pandas as pd
    >>> import numpy as np
    >>> data = np.array([np.arange(10)]*2).T  # 2 columns for x, y, and one for index
    >>> df_ = pd.DataFrame(data, columns=['x', 'y'])
    >>> train_x, val_x, test_x = \
             train_validate_test_split( df_, validation_set_size = 0.2, test_set_size = 0.2, a_seed = 1 )
    >>> train_x['x'].values
    array([0, 3, 1, 7, 8, 5])
    >>> val_x['x'].values
    array([4, 6])
    >>> test_x['x'].values
    array([2, 9])
    """
    validation_and_test_set_size = validation_set_size + test_set_size
    validation_and_test_split = validation_set_size / (test_set_size+validation_set_size)

    df_train_x, df_notTrain_x = train_test_split(pairs, test_size = validation_and_test_set_size, random_state = a_seed)

    df_test_x, df_val_x = train_test_split(df_notTrain_x, test_size = validation_and_test_split, random_state = a_seed)

    return df_train_x, df_val_x, df_test_x

if __name__ == '__main__':
    do_train()

