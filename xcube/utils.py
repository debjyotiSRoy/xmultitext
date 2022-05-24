# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_utils.ipynb (unless otherwise specified).

__all__ = ['namestr', 'list_files', 'make_paths', 'plot_reduction']

# Cell
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from fastcore.all import *
from .imports import *

# Cell
def namestr(obj, namespace):
    "Returns the name of the object `obj` passed"
    return [name for name in namespace if namespace[name] is obj]

# Cell
def list_files(startpath):
    """ simulates the linux tree cmd
    https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    """
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

# Cell
def make_paths(path, prefix=None):
    """
    with `path` as basedir, makes data and models dir and
    returns a dictionary of relevant pathlib objects
    """
    path_data = path/'data'
    path_model = path/'models'

    path_model.mkdir(exist_ok=True)
    path_data.mkdir(exist_ok=True)

    data = path_data/(prefix+'.csv')
    dls_lm_path, dls_lm_r_path = path_model/f"{prefix}_dls_lm.pkl", path_model/f"{prefix}_dls_lm_r.pkl"
    dls_lm_vocab_path, dls_lm_vocab_r_path = path_model/f"{prefix}_dls_lm_vocab.pkl", path_model/f"{prefix}_dls_lm_vocab_r.pkl"
    lm_path, lm_r_path = path_model/f"{prefix}_lm.pth", path_model/f"{prefix}_lm_r.pth"
    lm_finetuned_path, lm_finetuned_r_path = path_model/f"{prefix}_lm_finetuned.pth", path_model/f"{prefix}_lm_finetuned_r.pth"
    dsets_clas_path, dsets_clas_r_path = path_model/f"{prefix}_dset_clas.pkl", path_model/f"{prefix}_dset_clas_r.pkl"
    dls_clas_path, dls_clas_r_path = path_model/f"{prefix}_dls_clas.pkl", path_model/f"{prefix}_dls_clas_r.pkl"
    clas_path, clas_r_path = path_model/f"{prefix}_clas.pth", path_model/f"{prefix}_clas_r.pth"
    dls_colab_path = path_model/f"{prefix}_dls_colab.pkl"
    collab_path = path_model/f"{prefix}_collab.pth"
    plist = [path, path_data, path_model,
             data,
             dls_lm_path, dls_lm_r_path,
             dls_lm_vocab_path, dls_lm_vocab_r_path,
             lm_path, lm_r_path,
             lm_finetuned_path, lm_finetuned_r_path,
             dsets_clas_path, dsets_clas_r_path,
             dls_clas_path, dls_clas_r_path,
             clas_path, clas_r_path,
             dls_colab_path,
             collab_path]
    pdir = {}
    for o in plist:  pdir[namestr(o, locals())[0]] = o
    return pdir

# Cell
def plot_reduction(X, tSNE=True, n_comps=None, perplexity=30, figsize=(6,4)):
    """
    PCA on X and plots the first two principal components, returns the decomposition
    and the explained variances for each directions,
    if `tSNE` then does a tSNE after PCA.
    """
    reduction = "tSNE" if tSNE else "PCA"
    pca = PCA(n_components=n_comps, svd_solver="full")
    X_red = pca.fit_transform(X)
    if tSNE:
        tsne = TSNE(n_components=2, perplexity=perplexity)
        X_red = tsne.fit_transform(X_red[:, :50])
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1,1,1)
    plt.scatter(X_red[:, 0], X_red[:, 1], marker='x')
    ax.set_xlabel("1st component")
    ax.set_ylabel("2nd component")
    ax.set_title(f"{reduction} Decomposition")
    plt.show()
    return X_red, pca.explained_variance_ratio_