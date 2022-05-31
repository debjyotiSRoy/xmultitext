# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_collab.ipynb (unless otherwise specified).

__all__ = ['match_embeds', 'load_pretrained_keys', 'CollabLearner', 'collab_learner']

# Cell
from fastai.tabular.all import *
from fastai.collab import *

# Cell
def match_embeds(
    old_wgts:dict, # Embedding weights of the pretrained model
    old_vocab:list, # Vocabulary (tokens and labels) of the corpus used for pretraining
    new_vocab:dict # Current collab corpus vocabulary (`users` and `items`)
) -> dict:
    """
    Convert the `users` and `items` (possibly saved as `0.module.encoder.weight` and `1.attn.lbs_weight.weight` respectively)
    embedding in `old_wgts` to go from `old_vocab` to `new_vocab`
    """
    u_bias, u_wgts = None, old_wgts.get('0.module.encoder.weight')
    print(f"{u_wgts.shape = }")
    i_bias, i_wgts = old_wgts.get('1.attn.lbs_bias.weight', None), old_wgts.get('1.attn.lbs_weight.weight')
    print(f"{i_wgts.shape = }")
    u_wgts_m, i_wgts_m = u_wgts.mean(0), i_wgts.mean(0)
    new_u_wgts = u_wgts.new_zeros((len(new_vocab['token']), u_wgts.size(1)))
    new_i_wgts = i_wgts.new_zeros((len(new_vocab['label']), i_wgts.size(1)))
    if u_bias is not None:
        u_bias_m = u_bias.mean(0)
        new_u_bias = u_bias.new_zeros((len(new_vocab['token']), 1))
    if i_bias is not None:
        i_bias_m = i_bias.mean(0)
        new_i_bias = i_bias.new_zeros((len(new_vocab['label']), 1))
    u_old = old_vocab[0]
    u_old_o2i = u_old.o2i if hasattr(u_old, 'o2i') else {w:i for i,w in enumerate(u_old)}
    i_old = old_vocab[1]
    i_old_o2i = i_old.o2i if hasattr(i_old, 'o2i') else {w:i for i,w in enumerate(i_old)}
    u_miss, i_miss = 0, 0
    for i,w in enumerate(new_vocab['token']):
        idx = u_old_o2i.get(w, -1)
        new_u_wgts = u_wgts[idx] if idx>=0 else u_wgts_m
        if u_bias is not None: new_u_bias[i] = u_bias[idx] if idx>=0 else u_bias_m
        if idx == -1: u_miss = u_miss + 1
    for i,w in enumerate(new_vocab['label']):
        idx = i_old_o2i.get(w, -1)
        new_i_wgts = i_wgts[idx] if idx>=0 else i_wgts_m
        if i_bias is not None: new_i_bias[i] = i_bias[idx] if idx>=0 else i_bias_m
        if idx == -1: i_miss = i_miss + 1
    old_wgts['0.module.encoder.weight'] = new_u_wgts
    if '0.module.encoder_dp.emb.weight' in old_wgts: old_wgts['0.module.encoder_dp.emb.weight'] = new_u_wgts.clone()
    if u_bias is not None: pass
    old_wgts['1.attn.lbs_weight.weight'] = new_i_wgts
    if '1.attn.lbs_weight_dp.emb.weight' in old_wgts: old_wgts['1.attn.lbs_weight_dp.emb.weight'] = new_i_wgts.clone()
    if i_bias is not None: old_wgts['1.attn.lbs_bias.weight'] = new_i_bias
    return old_wgts, u_miss, i_miss

# Cell
def load_pretrained_keys(
    model, # Model architecture
    wgts:dict # Model weights
) -> tuple:
    "Load relevant pretrained `wgts` in `model"
    sd = model.state_dict()
    u_wgts, u_bias = wgts.get('0.module.encoder.weight', None), None
    if u_wgts is not None: sd['u_weight.weight'].data = u_wgts.data
    if u_bias is not None: sd['u_bias.weight'].data = u_bias.data
    i_wgts, i_bias = wgts.get('1.attn.lbs_weight.weight', None), wgts.get('1.attn.lbs_bias.weight', None)
    if i_wgts is not None: sd['i_weight.weight'].data = i_wgts.data
    if i_bias is not None: sd['i_bias.weight'].data = i_bias.data
    return model.load_state_dict(sd)

# Cell
class CollabLearner(Learner):
    "Basic class for a `Learner` in Collab."
    @delegates(save_model)
    def save(self,
        file:str, # Filename for the state_directory of model
        **kwargs):
        """
        Save model and optimizer state (if `with_opt`) to `self.path/self.model_dir/file`
        Save `self.dls.classes` to `self.path.self.model_dir/collab_vocab.pkl`
        """
        model_file = join_path_file(file, self.path/self.model_dir, ext='.pth')
        vocab_file = join_path_file(file+'_vocab', self.path/self.model_dir, ext='.pkl')
        save_model(model_file, self.model, getattr(self,'opt', None), **kwargs)
        save_pickle(vocab_file, self.dls.classes)
        return model_file

    def load_vocab(self,
        wgts_fname:str, #Filename of the saved weights
        vocab_fname:str, # Saved vocabulary filename in pickle format
        model=None # Model to load parameters from, deafults to `Learner.model`
    ):
        "Load the vocabulary (`users` and/or `items`) from a pretrained model and adapt it to the collab vocabulary."
        old_vocab = load_pickle(vocab_fname)
        new_vocab = self.dls.classes
        distrib_barrier()
        wgts = torch.load(wgts_fname, map_location=lambda storage,loc: storage)
        if 'model' in wgts: wgts = wgts['model'] # Just in case the pretrained model was saved with an optimizer
        wgts, *_ = match_embeds(wgts, old_vocab, new_vocab)
        load_pretrained_keys(self.model if model is None else model, wgts)
        return self

# Cell
@delegates(Learner.__init__)
def collab_learner(dls, n_factors=50, use_nn=False, emb_szs=None, layers=None, config=None, y_range=None, loss_func=None, pretrained=False, **kwargs):
    "Create a Learner for collaborative filtering on `dls`."
    emb_szs = get_emb_sz(dls, ifnone(emb_szs, {}))
    if loss_func is None: loss_func = MSELossFlat()
    if config is None: config = tabular_config()
    if y_range is not None: config['y_range'] = y_range
    if layers is None: layers = [n_factors]
    if use_nn: model = EmbeddingNN(emb_szs=emb_szs, layers=layers, **config)
    else:      model = EmbeddingDotBias.from_classes(n_factors, dls.classes, y_range=y_range)
    learn = CollabLearner(dls, model, loss_func=loss_func, **kwargs)
    if pretrained:
        try: fnames = [list(learn.path.glob(f'**/clas/*clas*.{ext}'))[0] for ext in ['pth', 'pkl']]
        except: IndexError: print(f'The model in {learn.path} is incomplete, re-train it'); raise
        learn = learn.load_vocab(*fnames, model=learn.model)
    return learn