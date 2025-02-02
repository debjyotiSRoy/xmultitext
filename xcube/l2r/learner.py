# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/09_l2r.learner.ipynb.

# %% auto 0
__all__ = ['L2RLearner', 'get_learner']

# %% ../../nbs/09_l2r.learner.ipynb 2
from fastai.torch_imports import *
from fastai.learner import *
from fastai.optimizer import *
from fastai.torch_core import *
from fastcore.all import *
from ..imports import *
from ..metrics import *
from .gradients import *

# %% ../../nbs/09_l2r.learner.ipynb 6
class L2RLearner:
    def __init__(self, model, dls, grad_func, loss_func, lr, cbs, opt_func=SGD, path=None):
        store_attr(but='cbs')
        self.path = Path(path) if path is not None else getattr(dls, 'path', Path('.'))
        self.cbs = L()
        self.add_cbs(cbs)

    def add_cb(self, cb):
        cb.learn = self
        setattr(self, cb.name, cb)
        self.cbs.append(cb)
        return self

    def add_cbs(self, cbs):
        L(cbs).map(self.add_cb)
        return self
        
    def one_batch(self, *args, **kwargs):
        self('before_batch')
        self.preds = self.model(self.xb)
        if self.model.training: # training
            srtd_preds, lambda_i = self.grad_func(self.preds, self.xb)
            srtd_preds.backward(lambda_i)
            
            self('after_backward')
            
            # free memory
            lambda_i = None
            import gc; gc.collect()
            torch.cuda.empty_cache()
            
            self.opt.step()
            self.opt.zero_grad()
            
        self('after_batch')
        
    def one_epoch(self, train, **kwargs):
        self.model.training = train
        self.dl = self.dls.train if train else self.dls.valid
        (self._do_epoch_validate, self._do_epoch_train)[self.model.training](**kwargs)
        
    def _do_epoch_train(self, *args, **kwargs):
        self('before_train')
        self._all_batches(*args, **kwargs)
        self('after_train')
        
    def _do_epoch_validate(self, *args, idx=1, dl=None, **kwargs):
        if dl is None: dl = self.dls[idx]
        self.dl = dl
        with torch.no_grad():
            self('before_validate')
            self._all_batches(*args, **kwargs)
            self('after_validate')
        
    def _all_batches(self, *args, **kwargs):
        for self.iter_num, self.xb in enumerate(self.dl):
            self.one_batch(*args, **kwargs)
    
    def create_opt(self):
        self.opt = self.opt_func(self.model.parameters(), self.lr)
        # self.opt.clear_state()
        return self.opt
    
    def fit(self, n_epochs, **kwargs):
        opt = getattr(self, 'opt', None)
        if opt is None: self.create_opt()
        self.n_epochs = n_epochs
        self('before_fit')
        try:
            for self.epoch,_ in enumerate(range(self.n_epochs)):
                self('before_epoch')
                self.one_epoch(True, **kwargs)
                self.one_epoch(False, **kwargs)
                self('after_epoch')
        except CancelFitException: pass 
        self('after_fit')
    
    def validate(self, idx=1, dl=None, **kwargs):
        try: 
            self.model.training = False
            self._do_epoch_validate(idx, dl, **kwargs)
        except CancelFitException: pass
    
    def __call__(self, name):
        for cb in self.cbs: getattr(cb, name, noop)()

# %% ../../nbs/09_l2r.learner.ipynb 8
@patch
@delegates(save_model)
def save(self:L2RLearner, file, **kwargs):
    "Save model and optimizer state (if 'with_opt') to `self.path/file`"
    file = join_path_file(file, self.path, ext='.pth')
    save_model(file, self.model, getattr(self, 'opt', None), **kwargs)
    return file

# %% ../../nbs/09_l2r.learner.ipynb 9
@patch
@delegates(load_model)
def load(self:L2RLearner, file, device=None, **kwargs):
    "Load model and optimizer state (if `with_opt`) from `self.path/file` using `device`"
    if device is None and hasattr(self.dls, 'device'): device = self.dls.device
    self.opt = getattr(self, 'opt', None)
    if self.opt is None: self.create_opt()
    file = join_path_file(file, self.path, ext='.pth')
    load_model(file, self.model, self.opt, device=device, **kwargs)
    return self

# %% ../../nbs/09_l2r.learner.ipynb 11
def get_learner(model, dls, grad_fn=rank_loss3, loss_fn=loss_fn2, lr=1e-5, cbs=None, opt_func=partial(SGD, mom=0.9), lambrank=False):
    if lambrank: grad_fn = partial(grad_fn, lambrank=lambrank)
    learner = L2RLearner(model, dls, grad_fn, loss_fn, lr, cbs, opt_func=opt_func)
    return learner
