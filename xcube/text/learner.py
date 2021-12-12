# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_text.learner.ipynb (unless otherwise specified).

__all__ = ['text_classifier_learner']

# Cell
from fastai.basics import *
from .models.core import *

# Cell
def _get_text_vocab(dls):
    vocab = dls.vocab
    if isinstance(vocab, L): vocab = vocab[0]
    return vocab

# Cell
def text_classifier_learner(dls, arch, seq_len=72, config=None, backwards=False, pretrained=True, drop_mult=0.5, n_out=None,
                           lin_ftrs=None, ps=None, max_len=72*20, y_range=None, **kwargs):
    "Create a `Learner` with a text classifier from `dls` and `arch`."
    vocab = _get_text_vocab(dls)
    if n_out is None: n_out = get_c(dls)
    assert n_out, "`n_out` is not defined, and could not be inferred from the data, set `dls.c` or pass `n_out`"
