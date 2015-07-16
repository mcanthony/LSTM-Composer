#Imports
import dataUtils, modelUtils
import numpy as np
import os, time, sys

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM
from keras.callbacks import ModelCheckpoint

#We need to ensure we're using Python 2.7.x for it to work
if sys.version_info[0] is not 2 and sys.version_info[1] is not 7:
	print("Please run this program with Python 2.7")
	sys.exit(-1)

DICE = False
if "DICE" in os.environ and os.environ["DICE"] == '1':
	DICE = True

if DICE == False:
	print("Running on personal computer...")
	dataset_path = "/Users/Bernat/Dropbox/UoE/Dissertation/midiFiles/"
	test_path = "/Users/Bernat/Dropbox/UoE/Dissertation/testMidi/"
else:
	print("Running on DICE...")
	dataset_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/midiFiles/"
	test_path = "/afs/inf.ed.ac.uk/user/s14/s1471922/Dissertation/testMidi/"


#Load data
print("Loading data...")
roll = dataUtils.createRepresentation(limitSongs=20) #array of "piano roll" like representations

#Transform 
print("Creating output sequences...")
step = 50
X, Y = dataUtils.createModelInputs(roll, padding=True, step=step, inc=1)
X, Y, notesMap = dataUtils.compressInputs(X, Y)
input_dim = len(notesMap)

#Training data shape:
# X -> (nb_samples, timesteps, input_dim) => "sequences of tones"
# Y -> (nb_samples, input_dim) => "next tone for every sequence"

#Build model
print("Building model...")
model = Sequential()
model.add(LSTM(input_dim, input_dim*2, return_sequences=True))
model.add(Dense(input_dim*2, input_dim*2))
model.add(LSTM(input_dim*2, input_dim))


print("Compiling model...")
model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

#Train
print("Training...")
checkpointer = ModelCheckpoint(filepath="%stempmodel%d.h5" % (test_path, int(time.time())), verbose=1, save_best_only=True)
history = modelUtils.LossHistory()
model.fit(X, Y, batch_size=1, nb_epoch=100, callbacks=[checkpointer, history])

#Save model
print("Saving model...")
currentTime = int(time.time())
model.save_weights("%smodel%d.h5" % (test_path, currentTime))

#Predict
print("Composing new song...")
(song, energy) = modelUtils.generateSong(model, X[step])

#Save data to representation and midi formats
print("Storing song representation")
dataUtils.saveRepresentation(song, "songoutput%d.nn" % (currentTime))
print("Storing song in midi format")
dataUtils.roll2midi(song)
print("Loss history")
print(history.losses)
dataUtils.saveRepresentation(history.losses, "losses%d.nn" % (currentTime))


print "Finished execution at time %d" % (currentTime)
