# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_metrics.ipynb (unless otherwise specified).

__all__ = ['PrecisionK', 'PrecisionR']

# Cell
from fastai.data.all import *
from fastai.metrics import *

# Cell
def PrecisionK(yhat_raw, y, k=15):
    """
        Inputs:
            yhat_raw: activation matrix of ndarray and shape (n_samples, n_labels)
            y: binary ground truth matrix of type ndarray and shape (n_samples, n_labels)
            k: for @k metric
    """
    yhat_raw, y = to_np(yhat_raw), to_np(y)
    # num true labels in the top k predictions / k
    sortd = yhat_raw.argsort()[:,::-1]
    topk = sortd[:, :k]

    # get precision at k for each sample
    vals = []
    for i, tk in enumerate(topk):
        num_true_in_top_k = y[i,tk].sum()
        vals.append(num_true_in_top_k / float(k))

    return np.mean(vals)

# Cell
def PrecisionR(yhat_raw, y):
    """
        Inputs:
            yhat_raw: activation matrix of ndarray and shape (n_samples, n_labels)
            y: binary ground truth matrix of type ndarray and shape (n_samples, n_labels)
    """
    yhat_raw, y = to_np(yhat_raw), to_np(y)
    # num true labels in the top r predictions / r, where r = number of labels associated with that sample
    sortd = yhat_raw.argsort()[:, ::-1]

    # get precision at r for each sample
    vals = []
    for i, sorted_activation_indices in enumerate(sortd):
        # compute the number of labels associated with this sample
        r = int(y[i].sum())
        top_r_indices = sorted_activation_indices[:r]
        num_true_in_top_r = y[i, top_r_indices].sum()
        vals.append(num_true_in_top_r / float(r))

    return np.mean(vals)