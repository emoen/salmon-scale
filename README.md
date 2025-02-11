# Automatic interpretation of salmon scales using deep learning

## Abstract
1. Determining the age structure of a fish species is important for understanding population and ecosystem dynamics and for stock assessment and management. For Atlantic salmon, age and other important biological information is collected from scale samples through manual qualitative interpretation. Reliable automatic methods are so far not widely utilised. 
2. We use a state of the art Convolutional Neural Network (CNN) architecture called EfficientNet and a novel data set consisting of 9056 images of salmon scales to train different CNNs for four different prediction tasks. We consider two binary classification tasks regarding the origin of the fish (wild/farmed) and the spawning state (spawner/non-spawner) as well as two regression tasks predicting the number of years spent in the river and the sea. We take advantage of transfer learning by starting our training process with a CNN pre-trained on existing open-access image database ImageNet. To further test the predictive performance of our two regression CNNs, a set of 150 additional salmon scale images were analyzed for river and sea age both by the CNNs and by six human expert readers.
3. We find that the CNNs perform well on the two binary classification tasks and on predicting sea age, while the prediction of river age is less accurate. Estimates of river age by experts exhibit higher variance and lower levels of agreement compared to sea age, and may indicate why this task is also more difficult for the CNN. We see substantial benefit in using transfer learning.  Comparing the performance of the CNN to six expert readers using standard precision measures for age reading, we confirmed the high performance of the CNN predicting sea age, well within the top of human expertise.
4. Automatic interpretation of scales offers a cost-efficient and effective way of investigation of fish age and life-history traits, which may further support the management of these biological resources.

## salmon-scale CNN results

Comparison of different metrics for prediction of salmon scales. I have also added metric from Greenland otolith prediction for comparison. The metrics is from the validation set. Except the first line which is from Greenland Halibut and is calculated from mean of pairs of right and left otolith. <br />
* In the wild/farmed dataset there is 5427 wild salmon, and 505 (8.5%) farmed salmon. Salmon classified as something else like unknown or trout are not included in training. 
* In the spawning/non-spawning dataset there is 8835 non-spanwning scales and 238 spawned scales (2.6%). Note: There is spawners 422 (4.6%) but missing images for 184 of these. Therefore they are not included in the training set.

(MAPE: Mean absolute percentage error)<br />
(MCC: mathews correlation coefficient)<br />

| Species              | Predict    |testLOSS| MSE  | MAPE | ACC | MCC |#trained |activ. f| classWeights |
| ---------------------| -----------|--------|------|------|-----|-----|---------|--------|--------------|
| Greenland Halibut(1) | age        | x      |2.65  |0.124 |0.262|x    |8875     | linear | x | 
| Greenland Halibut(2) | age        | -"-    |2.82  |0.136 |0.294|x    |8875     | linear | x |
| Salmon               | sea age    | -"-    |0.239 |0.141 |0.822|x    |9056     | linear | x |
| Salmon B4(12)        | sea age    | 1.476  |1.476 |60.25 |0.471|x    |9056     | linear | x |
| Salmon B4(13)        | sea age    | 0.17   |0.173 |8.97  |0.846|x    |8286     | linear | x |
| **Salmon B4 v1.1.0** | sea age  | 0.1570  |0.1570 |8.6405  |0.8699|x    |8286     | linear | x |
| **Salmon B4(14)patience20** | sea age  | 0.158  |0.158 |7.88  |0.863|x    |8286     | linear | x |
| **Salmon B4(14)rerun(lr=0.00007)** | sea age  | 0.158  |0.158 |7.1598 |0.864|x    |8286     | linear | x |
| **Salmon B4(14)rerun(lr=0.00007) seed=9** | sea age  | 0.199  |0.199 |7.1524 |0.863|x    |8286     | linear | x |
| **Salmon B4(14)rerun(lr=0.00007) no weights** | sea age  | 1.08  |1.08 |53.9 |0.496|x    |8286     | linear | x |
| Salmon B4(15)path20batch16| sea age|x  |x |x |x|x    |8299     | linear | x |
| Salmon               | river age  | -"-    |0.431 |0.252 |0.585|x    |6300     | linear | x |
| Salmon B4(9)         | river age  |2.35    |2.35  |x     |0.37 |x    |9056     | linear | x |
| Salmon B4(11)        | river age  |0.359   |0.359 |19.58 |0.618|x    |6238     | linear | x |
| **Salmon B4 v1.1.0**     | river age  |0.336   |0.336 |17.34 |0.632|x    |6238     | linear | x |
| **Salmon B4(16)patience20** | river age|0.359  |0.359 |17.315 |0.6297|x    |6238     | linear | x |
| **Salmon B4(16) rerun(lr=0.00008)** | river age|0.3237  |0.3237 |17.47 |0.6371|x    |6238     | linear | x |
| **Salmon B4(16) rerun(lr=0.00008) seed=9** | river age|0.3884  |0.3884 |17.11 |0.6339|x    |6238     | linear | x |
| **Salmon B4(16x) rerun(lr=0.00008) no weights** | river age|0.4896  |0.4896 |26.70 |0.5347|x    |6238     | linear | x |
| Salmon missing_loss1 | river & sea|9.4372  |2.955 |0.97  |0.707|x    |9056     | linear | x |
| Salmon missing_loss2 | river & sea|0.5915  |2.992 |0.974 |0.707|x    |9056     | linear | x |
| Salmon missing_loss3 | river & sea|2.0107  |2.011 |0.744 |0.607|x    |9056     | linear | x |
| Salmon (3)           | Spawned    |0.113   |x     |x     |0.964|x    |9056     | softmax| {0: 0.5, 1: 19} |
| Salmon (5)           | Spawned    |0.132   |x     |x     |0.958|x    |476      | softmax| {0: 1, 1: 1} |
| Salmon (8)           | spawned    |0.6417  |x     |x     |0.944|x    |476      | sigmoid| {0: 1, 1: 1} |
| Salmon (18)           | spawned    |x  |x     |x     |x|x    |9056      | softmax| {0: 0.5, 1: 19} |
| Salmon (6)           | Wild/farmed|0.155   |x     |x     |0.9697|x   |5917     | softmax| {0: 5.87, 1: 0.54} |
| **Salmon batch=8**           | Wild/farmed|0.187   |x     |x     |0.967|x   |5919     | softmax| {0: 5.87, 1: 0.54} |
| Salmon (10)lr=0.0005 | Wild/farmed|1.21    |x     |x     |0.924 |x   |5919     | softmax| {0: 5.87, 1: 0.54} |
| Salmon (4)           | Wild/farmed|0.213   |x     |x     |0.94 |x    |1010     | softmax| {0: 1, 1: 1} |
| Salmon (7)           | Wild/farmed|0.693   |x     |x     |0.075|x    |5919     | sigmoid| {0: 5.87, 1: 0.54} |
| Salmon (17)           | Wild/farmed|0.2057   |x     |x     |0.96292|x    |5919     | softmax| {0: 5.87, 1: 0.54} |


* (1) is test-set <br/>
* (2) is validation-set <br/>
* (3) train/val/test size: 70, 15, 15
  * 
  *
  * Training-set (negative example, positive example): (4861, 129)
  * Validation-set (negative example, positive example): (3541 89) - 89/(3541+89)= 0.025, 1-0.25 = 0.975
* (4) train/val/test size: 70, 15, 15
  * val_acc: 0.9276
  * class frequency: {vill:505, oppdrett:505}
  * CNN: efficientNet-B4, 380x380
  *
  * Training-set (negative example, positive example) (0,1), (1,0): (3772 2579) - 3772/(3772+2579) = 3772/6351=0.59
  * Validation-set (negative example, positive example)(0,1), (1,0): (809 552) - 809/(552+809)= 0.59
  * test-set (negative example, positive example)(0,1), (1,0): (809 552)
* missing_loss1 - missing_mse(y_true, y_pred) in https://github.com/emoen/salmon-scale/blob/master/mse_missing_values.py <br />
* missing_loss2 - missing_mse2(y_true, y_pred) in https://github.com/emoen/salmon-scale/blob/master/mse_missing_values.py <br />
* missing_loss3 - classic mse with 2 outputs <br />
* (9) regression on river age contains missing values - encoded as -1
* (10) identical to (6) but with lr=.0005 instead of the usual lr=.0001
* (11) identical to (9) but without scales of unknown river age. Learning rage 0.0001
* (12) without unknown using patience 5, on efficientNet B4. Resolution 380x380
* (14) patience 20, batch size=12, lr=0.0001, efficientNet B4, dense(2) linear, tensorboard_path='./tensorboard_salmon_sea_uten_ukjent_patience_20'
* (14) sea age: checkpoints_salmon_sea_uten_ukjent_patience_20 
* (16) river age: NB have forgotten to set new directory: checkpoints_salmon_sea_uten_ukjent. Patience 20
  * rerun: batch size=12
* (16x) river age: Same as (16) but with no weights. 150 epochs, 1600 steps and batch size of 12. 150 * 1600 * 12 = 2.880.000 images looked at in 150 epochs. 6246 images augmented by rotation of 360 degrees with mirroring which results in 360 * 2  * 6246 = 4.497.120 possible images. Best epoch was in epoch 122.
* (17) farmed: tensorboard_farmed_uten_ukjent_patience_20
* (18) Spawned: tensorboard_spawned_uten_ukjent_patience_20

Note val_acc is 0.7068 in almost every epoch (except 2. epoch of missing_loss2 training.) <br />

Missing_loss1/2 is same the same network - but with Dense(2, 'linear') so it predicts both sea and river age.

* Farmed salmon:(4) Precision, recall and f1-score from scikit-learn: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|opprett     |0.95	    |0.93	 |0.94	   |76     |
|vill        |0.93     |	0.95 |	0.94	  |75     |
|micro avg   |0.94	    |0.94	 |0.94	   |151    |
|macro avg   |0.94	    |0.94  |	0.94   |	151   |
|weighted avg|0.94	    |0.94  |	0.94   |	151   |  

Confusion matrix:

|class   |oppdrett|vill|
|--------|--------|----|
|oppdrett|71      |5   |
|vill    |4       |71  |

* Farmed salmon:(7) Precision, recall and f1-score from scikit-learn: 

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|opprett     |0.08	    |1.00	 |0.14	   |66     |
|vill        |0.00     |	0.00 |	0.00	  |823    |
|accuracy    |    	    |	     |0.08	   |890    |
|macro avg   |0.94	    |0.94  |	0.94   |890    |
|weighted avg|0.01	    |0.08  |	0.01   |890    |  

Confusion matrix:

|class   |oppdrett|vill|
|--------|--------|----|
|oppdrett|67      |0   |
|vill    |823     |0  |

* Farmed salmon:(6) Precision, recall and f1-score from scikit-learn: 

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|opprett     |0.87	    |0.70	 |0.78	   |67     |
|vill        |0.98     |	0.99 |0.98	   |823    |
|accuracy    |    	    |	     |0.97	   |890    |
|macro avg   |0.92	    |0.85  |0.88    |890    |
|weighted avg|0.97	    |0.97  |0.97    |890    |  

confusion matrix:

|class   |oppdrett|vill|
|--------|-------|-----|
|oppdrett|47     |20   |
|vill    |7      |816  |


* Spawner:(3) Precision, recall and f1-score from scikit-learn

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|Not spawnd  |0.99     | 0.98 |  0.98  | 1326  |
|spawnd      |0.35     |0.46  |  0.40  |   35  |
|accuracy    |	        |    	 |  0.96  | 1361  |
|macro avg   |0.67     | 0.72 |  0.69  | 1361  |
|weighted avg|0.97     | 0.96 |  0.97  | 1361  |  

confusion matrix:

|class     |non spawnd|spawnd|
|----------|--------|----|
|non spawnd|1296    |30  |
|spawnd    |19      |16  |

* Spawner:(5) Precision, recall and f1-score from scikit-learn

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|Not spawnd  |0.93     |1.00  |  0.96  | 38    |
|spawnd      |1.00     |0.91  |  0.95  | 33    |
|accuracy    |	        |    	 |  0.96  | 71    |
|macro avg   |0.96     | 0.95 |  0.96  | 71    |
|weighted avg|0.97     | 0.96 |  0.96  | 71    |  

confusion matrix:

|class     |non spawnd|spawnd|
|----------|--------|----|
|non spawnd|  38    |0   |
|spawnd    |   3    |30  |

* Spawner:(8) Precision, recall and f1-score from scikit-learn

|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|Not spawnd  |0.90     |1.00  |  0.95  | 38    |
|spawnd      |1.00     |0.88  |  0.94  | 33    |
|accuracy    |	        |    	 |  0.94  | 71    |
|macro avg   |0.95     | 0.94 |  0.94  | 71    |
|weighted avg|0.95     | 0.94 |  0.94  | 71    |  

confusion matrix:

|class     |non spawnd|spawnd|
|----------|--------|----|
|non spawnd|  38    |0   |
|spawnd    |   4    |29  |

* (17)
|            |precision|recall|f1-score|support|
|------------|---------|------|--------|-------|
|opprett     |0.76     |0.75  |  0.75  | 67    |
|not opprett |0.98     |0.98  |  0.98  | 823    |
|accuracy    |	        |    	 |  0.96  | 890   |
|macro avg   |0.87     | 0.86 |  0.87  | 890    |
|weighted avg|0.96     | 0.96 |  0.96  | 890    | 

|class   |oppdrett|vill|
|--------|-------|-----|
|oppdrett|50     |17   |
|vill    |16      |807  |

```
>>> df = pd.DataFrame({}, d2015.columns.values)
>>> df = df.append(d2015)
>>> df = df.append(d2016)
>>> df = df.append(d2017)
>>> df = df.append(d2018)
>>> df = df.append(d2016rb)
>>> df = df.append(d2017rb)
>>> len(df)
16601
>>> df.sjø.value_counts()
 2.0     7737
 1.0     3809
 3.0     2832
-1.0     1513
 4.0      486
 5.0      123
 6.0       59
 7.0       22
 8.0        9
 9.0        3
 11.0       1
 12.0       1
Name: sjø, dtype: int64
>>> df.smolt.value_counts()
-1.0    7923
 3.0    4900
 2.0    2937
 4.0     549
 1.0     216
 5.0      62
 6.0       8
Name: smolt, dtype: int64

```

Spawners in the dataset:
```
>>> d2015.gytarar.value_counts()
2-2-g-1                   3
2-3-g-1                   3
?-2-g-1-g                 1
2-2-g-2                   1
3-3-g-1                   1
2-2-g+                    1
?-2-g-1+                  1
3-2-g-1                   1
2-2-g-2 eller2-2-g-1-1    1
3-2-g-2                   1
Name: gytarar, dtype: int64
>>> d2015.gytarar.value_counts().sum()
14
>>> d2016.gytarar.value_counts().sum()
17
>>> d2017.gytarar.value_counts().sum()
24
>>> d2018.gytarar.value_counts().sum()
29
>>> d2016rb.gytarar.value_counts().sum()
112
>>> d2017rb.gytarar.value_counts().sum()
226
>>> 14+17+24+29+112+226
422
>>>
```

River age distribution:
```
>>> unique, counts = np.unique(all_smolt_age, return_counts=True)
>>> dict(zip(unique, counts))
{-1.0: 2827, 1.0: 195, 2.0: 2097, 3.0: 3528, 4.0: 377, 5.0: 45, 6.0: 4}
```

Sea age:
```
>>> unique, counts = np.unique(all_sea_age2, return_counts=True)
>>> dict(zip(unique, counts))
{1.0: 2323, 2.0: 4192, 3.0: 1443, 4.0: 235, 5.0: 64, 6.0: 31, 7.0: 8, 8.0: 2, 9.0: 1}
```
