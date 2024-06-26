import tensorflow as tf
#import keras as tfk
import numpy as np

class graph_object(object):
    def __init__(self):
        self.init=0

def Get_Inputs(GO,self):
    # Setup Placeholders .compat.v1.placeholder
    
    #GO.X = tf.placeholder(tf.float32, [None, self.imgs.shape[1], self.imgs.shape[2], self.imgs.shape[3]], name='Input')
    GO.X = tf.compat.v1.placeholder(tf.float32, [None, self.imgs.shape[1], self.imgs.shape[2], self.imgs.shape[3]], name='Input')
    # GO.X = tf.placeholder(tf.float32, [None, self.img_dim_1, self.img_dim_2, self.img_dim_3], name='Input')
    # GO.prob = tf.placeholder_with_default(0.0, shape=(), name='prob')
    # GO.prob_multisample = tf.placeholder_with_default(0.0, shape=(), name='prob_multisample')
    # GO.Y = tf.placeholder(dtype=tf.float32, shape=[None, self.Y.shape[1]])
    # GO.class_weights = tf.placeholder(dtype=tf.float32, shape=[1, self.Y.shape[1]])
    GO.prob = tf.compat.v1.placeholder_with_default(0.0, shape=(), name='prob')
    GO.prob_multisample = tf.compat.v1.placeholder_with_default(0.0, shape=(), name='prob_multisample')
    GO.Y = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, self.Y.shape[1]])
    GO.class_weights = tf.compat.v1.placeholder(dtype=tf.float32, shape=[1, self.Y.shape[1]])

def Conv_Model(GO,kernel_size=(2,2),strides=(2,2),l1_units=12,l2_units=24,l3_units=32):
    #tf.conv2
    #conv = tf.layers.conv2d(GO.X, filters=l1_units, kernel_size=kernel_size, strides=strides, padding='valid', activation=tf.nn.relu)
    conv = tf.compat.v1.layers.conv2d(GO.X, filters=l1_units, kernel_size=kernel_size, strides=strides, padding='valid', activation=tf.nn.relu)
    #conv = tf.keras.layers.conv2d(GO.X, filters=l1_units, kernel_size=kernel_size, strides=strides, padding='valid', activation=tf.nn.relu)
    #conv = tfk.layers.Conv2D( filters=l1_units, kernel_size=kernel_size, strides=strides, padding='valid', activation=tf.nn.relu,input_shape= GO.X)
    GO.l1 = tf.identity(conv,'l1')
    conv = tf.compat.v1.layers.dropout(conv,GO.prob)

    conv = tf.compat.v1.layers.conv2d(conv, filters=l2_units, kernel_size=kernel_size, strides=strides, padding='valid',activation=tf.nn.relu)
    #conv = tfk.layers.Conv2D( filters=l2_units, kernel_size=kernel_size, strides=strides, padding='valid',activation=tf.nn.relu,input_shape= conv)
    GO.l2 = tf.identity(conv,'l2')
    conv = tf.compat.v1.layers.dropout(conv,GO.prob)

    conv = tf.compat.v1.layers.conv2d(conv, filters=l3_units, kernel_size=kernel_size, strides=strides, padding='valid',activation=tf.nn.relu)
    #conv = tfk.layers.Conv2D( filters=l3_units, kernel_size=kernel_size, strides=strides, padding='valid',activation=tf.nn.relu ,input_shape= conv)
    GO.l3 = tf.identity(conv,'l3')
    conv = tf.compat.v1.layers.dropout(conv,GO.prob)

    kernel_size = (30,30)
    strides = (1,1)
    conv = tf.compat.v1.layers.conv2d(conv, filters=l3_units, kernel_size=kernel_size, strides=strides, padding='same',activation=tf.nn.relu)
    #conv = tfk.layers.Conv2D( filters=l3_units, kernel_size=kernel_size, strides=strides, padding='same',activation=tf.nn.relu,input_shape= conv)
    GO.l4 = tf.identity(conv,'l4')
    conv = tf.compat.v1.layers.dropout(conv,GO.prob)
    return conv

def MultiSample_Dropout(X,num_masks=2,activation=tf.nn.relu,use_bias=True,
                       rate=0.25,units=12,name='ml_weights',reg=0.0):
    """
    Multi-Sample Dropout Layer

    Implements Mutli-Sample Dropout layer from "Multi-Sample Dropout for Accelerated Training and Better Generalization"
    https://arxiv.org/abs/1905.09788

    Inputs
    ---------------------------------------
    num_masks: int
        Number of dropout masks to sample from.

    activation: func
        activation function to use on layer

    use_bias: bool
        Whether to incorporate bias.

    rate: float
        dropout rate

    units: int
        Number of output nodes

    name: str
        Name of layer (tensorflow variable scope)

    reg: float
        alpha for l1 regulariization on final layer (feature selection)

    Returns
    ---------------------------------------

    output of layer of dimensionality [?,units]

    """
    out = []
    for i in range(num_masks):
        fc = tf.compat.v1.layers.dropout(X,rate=rate)
        if i==0:
            reuse=False
        else:
            reuse=True

        with tf.compat.v1.variable_scope(name,reuse=reuse):
            out.append(tf.compat.v1.layers.dense(fc,units=units,activation=activation,use_bias=use_bias,
                                       kernel_regularizer=tf.contrib.layers.l1_regularizer(reg)))
    return tf.reduce_mean(tf.stack(out),0)


def isru(x, l=-1, h=1, a=None, b=None, name='isru', axis=-1):
    lim = 4
    if a is None:
        _a = h - l
    else:
        _a = tf.Variable(name=name + '_a', initial_value=np.ones(np.array([_.value for _ in x.shape])[axis]) + a, trainable=True, dtype=tf.float32)
        _a = 2 ** isru(_a, l=-lim, h=lim)

    if b is None:
        _b = 1
    else:
        _b = tf.Variable(name=name + '_b', initial_value=np.zeros(np.array([_.value for _ in x.shape])[axis]) + b, trainable=True, dtype=tf.float32)
        _b = (2 ** isru(_b, l=-lim, h=lim))+1

    return l + (((h - l) / 2) * (1 + (x * ((_a + ((x ** 2) ** _b)) ** -(1 / (2 * _b))))))