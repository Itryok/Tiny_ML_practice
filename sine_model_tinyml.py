# -*- coding: utf-8 -*-
"""sine_model_TinyML.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gO9RCrleqMtwM2VXz6dFsI_9DHAYZ4dW
"""

!pip install tensorflow==2.7.0
!pip install grpcio==1.47.0
!pip install numpy>=1.2.0
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import math

samples=10000
seed = 42
np.random.seed(seed)
tf.random.set_seed(seed)

#Generate a uniformly distributed set of random numbers in the range 0 to 2*pi
x_values = np.random.uniform(low = 0 ,high = 2*math.pi,size = samples)
np.random.shuffle(x_values)

y_values = np.sin(x_values)

plt.plot(x_values,y_values,'b.')
plt.show()

#Noisy data : Representative of real world signals
y_values += 0.1*np.random.randn(*y_values.shape)
plt.plot(x_values,y_values,'b.')
plt.show()

#Split the data into training,validation and test set
train_split = int(0.6*samples)
test_split = int (0.2*samples+train_split)

x_train,x_val,x_test = np.split(x_values,[train_split,test_split])
y_train,y_val,y_test = np.split(y_values,[train_split,test_split])

assert(x_train.size+x_val.size+x_test.size)==samples
print(x_train.size,x_val.size,x_test.size)
plt.plot(x_train,y_train,'b.',label='Train')
plt.plot(x_val,y_val,'y.',label='Validation')
plt.plot(x_test,y_test,'r.',label='Test')
plt.legend()
plt.show()

#Building the neural network
from tensorflow.keras import layers
model_1 = tf.keras.Sequential()
model_1.add(layers.Dense(16,activation="relu",input_shape=(1,)))
model_1.add(layers.Dense(1))
model_1.compile(optimizer = "rmsprop",loss = "mse",metrics = ["mae"])
model_1.summary()

history_1 = model_1.fit(x_train,y_train,epochs=1000,batch_size=16,validation_data = (x_val,y_val))

loss = history_1.history['loss']
val_loss = history_1.history['val_loss']
epochs = range(1,len(loss)+1)
plt.figure(figsize=(10,7))
plt.plot(epochs,loss,'g.',label = 'Training loss')
plt.plot(epochs,val_loss,'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

skip =150
plt.figure(figsize=(20,15))
plt.plot(epochs[skip:],loss[skip:],'g.',label = 'Training loss')
plt.plot(epochs[skip:],val_loss[skip:],'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

mae = history_1.history['mae']
val_mae = history_1.history['val_mae']

plt.figure(figsize=(20,15))
plt.plot(epochs[skip:],mae[skip:],'g.',label = 'Training loss')
plt.plot(epochs[skip:],val_mae[skip:],'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('mae')
plt.legend()
plt.show()

#Plot network's predictions for the training data against the expected values
predictions = model_1.predict(x_train)
plt.clf()
plt.title('Training data predicted vs actual values')
plt.plot(x_test,y_test,'b.',label='Actual')
plt.plot(x_train,predictions,'r.',label='Predicted')
plt.legend()
plt.show()

model_2 = tf.keras.Sequential()
model_2.add(layers.Dense(16,activation='relu',input_shape=(1,)))
model_2.add(layers.Dense(16,activation='relu'))#May help the network learn more complex representations
model_2.add(layers.Dense(1))
model_2.compile(optimizer='rmsprop',loss='mse',metrics=['mae'])
model_2.summary()

history_2 = model_2.fit(x_train,y_train,epochs=700,batch_size=32,validation_data=(x_val,y_val))

loss = history_2.history['loss']
val_loss = history_2.history['val_loss']
epochs = range(1,len(loss)+1)
plt.figure(figsize=(10,7))
plt.plot(epochs,loss,'g.',label = 'Training loss')
plt.plot(epochs,val_loss,'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

skip =50
plt.figure(figsize=(20,15))
plt.clf()
plt.plot(epochs[skip:],loss[skip:],'g.',label = 'Training loss')
plt.plot(epochs[skip:],val_loss[skip:],'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

mae = history_2.history['mae']
val_mae = history_2.history['val_mae']

plt.figure(figsize=(20,15))
plt.plot(epochs[skip:],mae[skip:],'g.',label = 'Training loss')
plt.plot(epochs[skip:],val_mae[skip:],'b.',label = 'Validation loss')
plt.title("Training and Validation loss")
plt.xlabel('epochs')
plt.ylabel('mae')
plt.legend()
plt.show()

loss = model_2.evaluate(x_test,y_test)
predictions = model_2.predict(x_test)
plt.clf()
plt.title('Comparision of prediction and actual values')
plt.plot(x_test,y_test,'b.',label='Actual')
plt.plot(x_test,predictions,'g.',label='Predicted')
plt.legend()
plt.show()

#Converting the model to Tensorflow Lite format ithout Quantuzation
converter = tf.lite.TFLiteConverter.from_keras_model(model_2)
tflite_model = converter.convert()

#Saving the model to disk
open('sine_model.tflite',"wb").write(tflite_model)

#Converting the model to Tensorflow Lite format with quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model_2)
#Indicate that we want to perform default optimizations which include quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]

#Define a Generator function that provides our test data's x values as a representative dataset,
#and tell the converter to use it
def representative_dataset_generator():
  for val in x_test:
    #Each scalar value must be inside a 2D array that is wrapped in a list
    yield [np.array(val,dtype=np.float32,ndmin=2)]


"""On Windows, 'b' appended to the mode opens the file in binary mode, so there are also modes like 'rb', 'wb', and 'r+b'.
Python on Windows makes a distinction between text and binary files;
the end-of-line characters in text files are automatically altered slightly when data is read or written.
This behind-the-scenes modification to file data is fine for ASCII text files, but it’ll corrupt binary data like that in JPEG or EXE files.
converter.representative_dataset = representative_dataset_generator

When writing in binary mode, Python makes no changes to data as it is written to the file.
In text mode (when the b is excluded as in just w or when you specify text mode with wt), however,
Python will encode the text based on the default text encoding.
Additionally, Python will convert line endings (\n) to whatever the platform-specific line ending is,
which would corrupt a binary file like an exe or png file.

Text mode should therefore be used when writing text files (whether using plain text or a text-based format like CSV),
while binary mode must be used when writing non-text files like images.
"""

#Convert the model
tflite_model = converter.convert()

#Save the model to the disk
open('sine_model_quantized.tflite',"wb").write(tflite_model)

"""For running the TensorflowLite converted models we need TensorFlowLite Interpreter

To make predictions with our TensorFlowLite model we need to do the following :

1) Instantiate the Interpreter object

2) Call some methods that allocate memory for the model.

3) Write the input to the input tensor.

4) Invoke the model.

5) Read the output from the output tensor.

"""

#Instantiate an Interpreter for each model
sine_model = tf.lite.Interpreter('sine_model.tflite')
sine_model_quantized = tf.lite.Interpreter('sine_model_quantized.tflite')

#Allocate memory for each model
sine_model.allocate_tensors()
sine_model_quantized.allocate_tensors()

#Get indexes of the input and output tensors
sine_model_input_index = sine_model.get_input_details()[0]["index"]
sine_model_output_index = sine_model.get_output_details()[0]['index']
sine_model_quantized_input_index = sine_model_quantized.get_input_details()[0]["index"]
sine_model_quantized_output_index = sine_model_quantized.get_output_details()[0]['index']

#Create arrays to store the results
sine_model_predictions = []
sine_model_quantized_predictions = []

#Run each model's interpreter for each value and store the results in arrays
for x_value in x_test:
  #Create a 2D tensor wrapping the current x_value
  x_value_tensor = tf.convert_to_tensor([[x_value]],dtype=np.float32)
  #Write the value to the input tensor
  sine_model.set_tensor(sine_model_input_index,x_value_tensor)
  #Run inference
  sine_model.invoke()
  #Read the prediction from the output tensor
  sine_model_predictions.append(sine_model.get_tensor(sine_model_output_index)[0])

  #Repeating the same for the quantized interpreter model
  sine_model_quantized.set_tensor(sine_model_quantized_input_index,x_value_tensor)
  sine_model_quantized.invoke()
  sine_model_quantized_predictions.append(sine_model_quantized.get_tensor(sine_model_quantized_output_index)[0])

plt.clf()
plt.title('Comparision of various models against actual values')
plt.plot(x_test,y_test,'bo',label = 'Actual')
#plt.plot(x_test,predictions,'ro',label = 'Original predictions')
#plt.plot(x_test,sine_model_predictions,'rx',label= 'Lite predictions')
plt.plot(x_test,sine_model_quantized_predictions,'gx',label = 'Lite quantized predictions')
plt.legend()
plt.show()

#Compare the quantized and basic tflite model sizes
import os
basic_model_size = os.path.getsize('sine_model.tflite')
print('Basic model size is %d bytes'%basic_model_size)
quantized_model_size = os.path.getsize('sine_model_quantized.tflite')
print('Quantized model size is %d bytes'%quantized_model_size)
diff = basic_model_size - quantized_model_size
print('Difference is %d bytes'%diff)

"""More complex models have many more weights, meaning the space saving from quantization will be much higher, approaching 4x for most sophisticated models.

Regardless, our quantized model will take less time to execute than the original version, which is important on a tiny microcontroller!
"""

#install xxd
!apt-get -qq install xxd
#Save the file as a C source file
!xxd -i sine_model_quantized.tflite > sine_model_quantized.cc
#Print the source file
!cat sine_model_quantized.cc

