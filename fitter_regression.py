import os
import numpy as np
from argparse import ArgumentParser
from keras.utils.np_utils import to_categorical
from tauperf.imaging.load import load_test_data, print_sample_size


import logging
log = logging.getLogger(os.path.basename(__file__))
log.setLevel(logging.INFO)

parser = ArgumentParser()
parser.add_argument(
    '--no-train', default=False, action='store_true')
parser.add_argument(
    '--overwrite', default=False, action='store_true')
parser.add_argument(
    '--equal-size', default=False, action='store_true')
parser.add_argument(
    '--debug', default=False, action='store_true')
parser.add_argument(
    '--training-chunks', default=3, type=int)
parser.add_argument(
    '--one-prong-only', default=False, action='store_true')
parser.add_argument(
    '--dev', default=False, action='store_true')

args = parser.parse_args()

if args.debug:
    log.warning('')
    log.warning('DEBUG MODE ACTIVATED')
    log.warning('')

data_dir = os.path.join(os.getenv('DATA_AREA'), 'v13/test_regression_2')
                        
if args.one_prong_only:
    filenames = [
        os.path.join(data_dir, "images_new_1p0n.h5"),
        os.path.join(data_dir, "images_new_1p1n.h5"),
        os.path.join(data_dir, "images_new_1p2n.h5"),
        ]
    labels = ['1p0n', '1p1n', '1pXn']
    n_classes = 3
else: 
    filenames = [
        os.path.join(data_dir, "images_new_1p0n.h5"),
        os.path.join(data_dir, "images_new_1p1n.h5"),
        os.path.join(data_dir, "images_new_1p2n.h5"),
        os.path.join(data_dir, "images_new_3p0n.h5"),
        os.path.join(data_dir, "images_new_3p1n.h5"),
        ]
    labels = ['1p0n', '1p1n', '1pXn', '3p0n', '3pXn']
    n_classes = 5


print_sample_size(filenames, labels)

kine_features = ['pt', 'eta', 'phi']
features = kine_features + ['tracks', 's1', 's2', 's3', 's4', 's5']
reg_features = 'alpha_e' #'true_pt', 'true_eta', 'true_phi', 'true_m']


test, val, y_test, y_val = load_test_data(
    filenames, debug=args.debug)
y_val_cat = to_categorical(y_val, n_classes)
y_test = test[reg_features]


# ##############################################
if args.dev:
    model_filename = 'cache/regression_energy_{0}_chunks'.format(args.training_chunks)
    model_filename += '_{epoch:02d}_epochs.h5'
else:
    model_filename = 'cache/regression_energy.h5'

if args.no_train:
    log.info('loading model')
    from keras.models import load_model
    model = load_model(model_filename)
else:
    log.info('training...')
    from tauperf.imaging.models import *

    model = dense_merged_model_topo_with_regression(test, n_classes=n_classes, final_activation='softmax')
    from tauperf.imaging.utils import fit_model_gen

    metrics = 'mean_absolute_percentage_error'
    losses = 'mean_absolute_percentage_error'
    loss_weights = 1.
  
    fit_model_gen(
        model,
        filenames, features,
        val, y_val_cat,
        reg_features=reg_features,
        n_chunks=args.training_chunks,
        use_multiprocessing=False,
        workers=1,
        filename=model_filename,
        metrics=metrics,
        losses=losses,
        loss_weights=loss_weights,
        model_optimizer='adam',
        overwrite=args.overwrite,
        no_train=args.no_train, 
        equal_size=args.equal_size, 
        dev=args.dev,
        debug=args.debug)




# ##############################################
log.info('testing stuff')

log.info('compute classifier scores')

X_test  = [test[feat] for feat in features]
y_pred = model.predict(X_test, batch_size=32, verbose=1)
#y_pred = np.load('regression.npy')

# log.info('drawing the computer-vision confusion matrix')
# from sklearn.metrics import confusion_matrix
# from tauperf.imaging.plotting import plot_confusion_matrix

# cnf_mat = confusion_matrix(y_test, np.argmax(y_pred, axis=1))
# diagonal = float(np.trace(cnf_mat)) / float(np.sum(cnf_mat))

# from tauperf.imaging.plotting import plot_confusion_matrix, plot_roc
# plot_confusion_matrix(
#     cnf_mat, classes=labels, 
#     title='Confusion matrix, diagonal = {0:1.2f} %'.format(100 * diagonal),
#     name='plots/imaging/confusion_matrix_categorical.pdf')

# log.info('drawing the pantau confusion matrix')
# cnf_mat = confusion_matrix(y_test, test['pantau'])
# diagonal = float(np.trace(cnf_mat)) / float(np.sum(cnf_mat))
# plot_confusion_matrix(
#     cnf_mat, classes=labels, 
#     title='Pantau confusion matrix, diagonal = {0:1.2f} %'.format(100 * diagonal),
#     name='plots/imaging/confusion_matrix_reference.pdf')

# log.info('drawing the roc curves and pantau WP')
# from sklearn.metrics import roc_curve
# from tauperf.imaging.plotting import plot_roc
# plot_roc(y_test, y_pred, test['pantau'])
log.info('drawing the pt')
from tauperf.imaging.plotting import plot_reg
plot_reg(y_pred, test['true_pt'], test['pt'], test['e'])

log.info('job finished succesfully!')