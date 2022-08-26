import pandas as pd
import numpy as np
import concurrent.futures
from sklearn.preprocessing import  LabelEncoder
from sklearn.linear_model import LogisticRegression


from .Data_handler.datahandler import Datahandler
from .data_slicer.slice_finder import Slice, SliceFinder




def run_slice_finder(data_obj, K):

	X_train, X_test, Y_train, Y_test = data_obj.test_train_data()

	Y_train_pred, Y_test_pred = data_obj.test_train_pred_data()

	model_classes = data_obj.model.classes_

	print("initialise slice finder")
	sf = SliceFinder( (X_test, Y_test), Y_test_pred, model_classes)

	print("Started slicing")
	recommendations = sf.find_slice(K, degree=4, max_workers=8)

	# for s in recommendations:
	#     print("++++++++++++++++\n\n")
	#     print(s.slice_des)
	#     print("\n\n++++++++++++++++")

	return data_obj.decode_sf(recommendations)











if __name__ == "__main__":

	model = LogisticRegression()


	data_obj = Datahandler("../data/adult.csv",model)


	recommendations = run_slice_finder(data_obj, K = 5)


	count = 1
	for s in recommendations:
		print("\n###################\n")
		print("Slice description {}:".format(count))
		count += 1

		for k, v in list(s.slice_des.items()):
			print('%s : %s'%(k, v))

		print ('---------------------\nmetric: %s'%(s.metric))
		print ('size: %s'%(s.size))

		print(data_obj.violin_data(s.slice_index,tick = 0.1))



		


