from tensorflow.python.client import device_lib
import tensorflow as tf
import os

gpu = 0
os.environ["CUDA_DEVICE_ORDER"] = 'PCI_BUS_ID'
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

tf.device('/device:GPU:0')

def get_available_devices():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos]

print(get_available_devices())

gpus = tf.config.experimental.list_physical_devices('GPU')
print(gpus)

if gpus:     
    try:  
        tf.config.experimental.set_visible_devices(gpus[0], 'GPU') 
        print(gpus[0])
    except RuntimeError as e:         print(e)  

