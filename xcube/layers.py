# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_layers.ipynb (unless otherwise specified).

__all__ = ['Lin1BnDrop']

# Cell
from fastai.torch_imports import *
from fastai.layers import *

# Cell
class Lin1BnDrop(nn.Sequential):
    "Module grouping `BatchNorm1d`, `Dropout` and a `Linear` layer with just one output feature"
    def __init__(self, n_in, n_out, bn=True, p=0., act=None, lin_first=False):
        layers = [BatchNorm(n_in, ndim=1)] if bn else []
        if p != 0: layers.append(nn.Dropout(p))
        lin = [nn.Linear(n_out, 1, bias=not bn)]
        if act is not None: lin.append(act)
        layers = lin+layers if lin_first else layers+lin
        super().__init__(*layers)