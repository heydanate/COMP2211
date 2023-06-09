# -*- coding: utf-8 -*-
"""pa1_sentiment_analysis_knn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mucMc1RC_KxdNN_1yftgRsPaYOAdFt5_
"""

import numpy as np
import pandas as pd
import scipy.sparse as sparse
from scipy import stats


class KNNModel:
  def __init__(self, k, p):
    self.k = k
    self.p = p

  def fit(self, train_dataset, train_labels):
    self.train_dataset = train_dataset # shape: (num_train_samples, dimension)
    self.train_labels = train_labels # shape: (num_train_samples, )

  def compute_Minkowski_distance(self, test_dataset):
    # TODO
    minkowski_difference = np.abs(np.expand_dims(test_dataset, axis=1) - np.expand_dims(self.train_dataset, axis=0)) # shape: (num_test_samples, num_train_samples, dimension)
    dist = np.power(np.sum(np.power(minkowski_difference, self.p), axis=2), 1/self.p) # shape: (num_test_samples, num_train_samples)
    return dist # shape: (num_test_samples, num_train_samples)
    # pass  # delete this line when you write your code

  def find_k_nearest_neighbor_labels(self, test_dataset):
    # TODO
    minkowski = self.compute_Minkowski_distance(test_dataset) # shape: (num_test_samples, num_train_samples)
    knn_idx = np.argsort(minkowski, axis=1)[:, :self.k] # shape: (num_test_samples, self.k)
    k_nearest_neighbor_labels = np.take(self.train_labels, knn_idx) # shape: (num_test_samples, self.k)
    return k_nearest_neighbor_labels # shape: (num_test_samples, self.k)
    # pass  # delete this line when you write your code

  def predict(self, test_dataset):
    # TODO
    knn_labels = self.find_k_nearest_neighbor_labels(test_dataset)
    num_classes = np.max(self.train_labels) + 1
    test_predict = np.zeros(len(test_dataset), dtype=int)
    for i in range(len(test_dataset)):
        knnlabel, counts = np.unique(knn_labels[i], return_counts=True)
        index = np.argmax(counts) 
        label_idx = knnlabel[index] 
        test_predict[i] = label_idx
    return test_predict # shape: (num_test_samples, )
    # pass  # delete this line when you write your code


def generate_confusion_matrix(test_predict, test_labels):
  # TODO
  test_labels = test_labels.astype(int)
  test_predict = test_predict.astype(int)
  num_classes = np.amax(test_labels) + 1
  confusion_matrix = np.zeros((num_classes, num_classes), dtype=np.float64)
  
  for i in range(len(test_predict)):
    if test_labels[i] < num_classes and test_predict[i] < num_classes:
      confusion_matrix[test_labels[i], test_predict[i]] += 1
  return confusion_matrix # shape: (num_classes, num_classes)
  # pass  # delete this line when you write your code


def calculate_accuracy(test_predict, test_labels):
  # TODO
  confusion_matrix = generate_confusion_matrix(test_predict, test_labels)
  num_samples = len(test_labels)
  accuracy = np.sum(np.diagonal(confusion_matrix), dtype=np.float64) / num_samples
  return accuracy # dtype: float
  # pass  # delete this line when you write your code


def calculate_precision(test_predict, test_labels):
  # TODO
  confusion_matrix = generate_confusion_matrix(test_predict, test_labels)
  precision_eq = np.diagonal(confusion_matrix) / np.sum(confusion_matrix, axis=0, dtype=np.float64)
  precision = np.average(precision_eq)
  return precision # dtype: float
  # pass  # delete this line when you write your code


def calculate_recall(test_predict, test_labels):
  # TODO
  confusion_matrix = generate_confusion_matrix(test_predict, test_labels)
  recall_eq = np.diagonal(confusion_matrix) / np.sum(confusion_matrix, axis=1, dtype=np.float64)
  recall = np.average(recall_eq)
  return recall # dtype: float
  # pass  # delete this line when you write your code


def calculate_macro_f1(test_predict, test_labels):
  # TODO
  precision = calculate_precision(test_predict, test_labels)
  recall = calculate_recall(test_predict, test_labels)
  macro_f1 = 2 * precision * recall / (precision + recall)
  return macro_f1 # dtype: float
  # pass  # delete this line when you write your code


def calculate_MCC_score(test_predict, test_labels):
  # TODO
  confusion_matrix = generate_confusion_matrix(test_predict, test_labels)
  num_samples = np.sum(confusion_matrix)
  TP = np.diagonal(confusion_matrix)
  FP = np.sum(confusion_matrix, axis=0) - TP
  FN = np.sum(confusion_matrix, axis=1) - TP
  numerator = np.sum(TP * num_samples) - np.sum((TP + FP) * (TP + FN))
  denominator = np.sqrt((np.sum(num_samples**2) - np.sum((TP + FP)**2)) * (np.sum(num_samples**2) - np.sum((TP + FN)**2)))
  MCC_score = numerator / denominator
  return MCC_score # dtype: float
  # pass  # delete this line when you write your code


class DFoldCV:
  def __init__(self, X, y, k_list, p_list, d, eval_metric):
    self.X = X
    self.y = y
    self.k_list = k_list
    self.p_list = p_list
    self.d = d
    self.eval_metric = eval_metric

  def generate_folds(self):
    # TODO
    num_validation_samples = len(self.X) // self.d
    train_d_folds = []
    test_d_folds = []
    Xy = np.concatenate((self.X, self.y.reshape(-1, 1)), axis=1)  
    Xy_folds = np.array_split(Xy, self.d)  
    for i in range(self.d):
  
        test_fold = Xy_folds[i]
 
        train_folds = Xy_folds[:i] + Xy_folds[i+1:]
        train_fold = np.concatenate(train_folds, axis=0)

        X_train_fold = train_fold[:, :-1]
        y_train_fold = train_fold[:, -1]

        X_test_fold = test_fold[:, :-1]
        y_test_fold = test_fold[:, -1]

        train_d_folds.append(np.concatenate((X_train_fold, y_train_fold.reshape(-1, 1)), axis=1))
        test_d_folds.append(np.concatenate((X_test_fold, y_test_fold.reshape(-1, 1)), axis=1))
    return train_d_folds, test_d_folds # type: tuple
    # pass  # delete this line when you write your code
  
  def cross_validate(self):
    # TODO
    train_d_folds, test_d_folds = self.generate_folds()
    scores = np.zeros((len(self.k_list), len(self.p_list), self.d))
    for i, k in enumerate(self.k_list):
      for j, p in enumerate(self.p_list):
        knn_model = KNNModel(k, p)
        for fold in range(self.d):
          train_X = train_d_folds[fold][:, :-1]
          train_y = train_d_folds[fold][:, -1]
          test_X = test_d_folds[fold][:, :-1]
          test_y = test_d_folds[fold][:, -1]
          knn_model.fit(train_X, train_y)
          test_predict = knn_model.predict(test_X)
          scores[i, j, fold] = self.eval_metric(test_predict, test_y)
    return scores # shape: (length of self.k_list, length of self.p_list, self.d)
    # pass  # delete this line when you write your code

  def validate_best_parameters(self):
    # TODO
    scores = self.cross_validate()
    averagescores = np.average(scores, axis=2) 
    best_idxvalues = np.unravel_index(np.argmax(averagescores), averagescores.shape) 
    k_best = self.k_list[best_idxvalues[0]] 
    p_best = self.p_list[best_idxvalues[1]] 
    return k_best, p_best # type: tuple
    # pass  # delete this line when you write your code


### The following part can be deleted or be uncommented. Deleting or commenting out them would be the easiest way.
### If you do not want to comment them out, make sure all other codes are under the indent of if __name__ == '__main__'.
# if __name__ == '__main__':
#   train_dataset = sparse.load_npz("train_dataset.npz")
#   test_dataset = sparse.load_npz("test_dataset.npz")
#   train_dataset = train_dataset.toarray()
#   test_dataset = test_dataset.toarray()
#   train_labels = np.load("train_labels.npy")
#   test_labels = np.load("test_labels.npy")

#   knn_model = KNNModel(10, 2)
#   knn_model.fit(train_dataset, train_labels)
#   dist = knn_model.compute_Minkowski_distance(test_dataset)
#   print(f"The Minkowski distance between the first five test samples and the first five training samples are:\n {dist[ : 5, : 5]}") # should be [[1.40488545 1.41421356 1.40473647 1.41421356 1.40205505]
#                                                                                                                                     #            [1.40172965 1.41421356 1.40153004 1.41421356 1.39793611]
#                                                                                                                                     #            [1.40573171 1.41421356 1.40559629 1.41421356 1.40315911]
#                                                                                                                                     #            [1.40403747 1.41421356 1.40387491 1.41421356 1.40094856]
#                                                                                                                                     #            [1.41421356 1.39611886 1.41421356 1.39841935 1.41421356]]
#   k_nearest_neighbor_labels = knn_model.find_k_nearest_neighbor_labels(test_dataset)
#   print(f"The k nearest neighbor labels for the first five test samples are:\n {k_nearest_neighbor_labels[ : 5, :]}") # should be [[0 1 1 1 1 2 0 0 0 2]
#                                                                                                                       #            [2 1 1 0 0 0 0 0 0 0]
#                                                                                                                       #            [1 0 0 1 1 2 1 1 0 1]
#                                                                                                                       #            [1 1 0 2 2 1 0 1 1 0]
#                                                                                                                       #            [2 2 2 2 2 1 2 0 1 2]]
#   test_predict = knn_model.predict(test_dataset)
#   print(f"The predictions for test data are:\n {test_predict}") # should be [0 0 1 1 2 0 0 0 0 0 0 2 0 0 0 0 0 2 0 1 1 0 0 1 0 0 0 2 2 2 2 0 0 0 0 0 0
#                                                                 # 0 0 0 0 0 2 0 0 2 2 0 1 0 0 1 0 0 0 0 0 0 0 1 2 1 2 0 0 0 0 0 0 0 0 0 0 2
#                                                                 # 0 1 0 0 1 0 0 0 2 0 1 0 0 2 0 1 0 2 1 0 0 2 0 0 1 0]
#   confusion_matrix = generate_confusion_matrix(test_predict, test_labels)
#   print(f"The confusion matrix is:\n {confusion_matrix}") # should be [[48.  3.  1.]
#                                                           #             [16. 11. 10.]
#                                                           #             [ 4.  1.  6.]]
#   accuracy = calculate_accuracy(test_predict, test_labels)
#   print(f"The accuracy is: {accuracy}") # should be 0.65
#   precision = calculate_precision(test_predict, test_labels)
#   print(f"The macro average precision is: {precision}") # should be 0.5973856209150327
#   recall = calculate_recall(test_predict, test_labels) 
#   print(f"The macro average recall is: {recall}") # should be 0.5886095886095887
#   macro_f1 = calculate_macro_f1(test_predict, test_labels)
#   print(f"The macro f1 score is: {macro_f1}") # should be 0.5929651346720406
#   MCC_score = calculate_MCC_score(test_predict, test_labels)
#   print(f"The MCC score is: {MCC_score}") # should be 0.4182135132877802

#   k_list = [5, 10, 15]
#   p_list = [2, 4]
#   d = 10
#   dfoldcv = DFoldCV(train_dataset, train_labels, k_list, p_list, d, calculate_MCC_score)
#   scores = dfoldcv.cross_validate()
#   print(f"The scores for the first k value and the first p value: {scores[0, 0, :]}") # should be [0.35862701 0.44284459 0.32790457 0.39646162 0.21971336 0.3317104
#                                                                                       #            0.27405523 0.3728344  0.391094   0.41420285]
#   best_param = dfoldcv.validate_best_parameters()
#   print(f"The best K value and p value are: {best_param}") # should be (10, 2)