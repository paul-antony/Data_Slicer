import numpy as np
import pandas as pd
import json

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


class Datahandler:
	def __init__(self, fname, model, target_col_name=[]):

		self.model = model

		self.df = pd.read_csv(fname)
		self.df = self.df.dropna()

		if (len(target_col_name) != 0):
			self.target_col_name = target_col_name
		else:
			self.target_col_name = [self.df.columns[-1]]

		self.encoders = {}

		self.column_type = {x: True for x in self.df.columns}
		for column in self.df.columns:
			if self.df.dtypes[column] == np.object:
				self.column_type[column] = False
		self.column_type.pop(self.target_col_name[0])

		self.target_types = np.unique(self.df[self.df.columns[-1]])

		self.X_train, self.X_test, self.Y_train, self.Y_test = [], [], [], []
		self.Y_train_pred, self.Y_test_pred = [], []

		self.set_train_test_data()

		self.set_model_pred_data()

	def encode(self):
		df_copy = self.df.copy()
		encoders = {}
		for column in df_copy.columns:
			if df_copy.dtypes[column] == np.object:
				le = LabelEncoder()
				df_copy[column] = le.fit_transform(df_copy[column])
				encoders[column] = le
		self.encoders = encoders
		return df_copy

	def test_train_data(self):

		return self.X_train.copy(), self.X_test.copy(), self.Y_train.copy(), self.Y_test.copy()

	def test_train_pred_data(self):
		return self.Y_train_pred.copy(), self.Y_test_pred.copy()

	def set_model_pred_data(self):

		self.model.fit(self.X_train, self.Y_train)

		temp = self.X_test.copy()
		temp["y_pred"] = self.model.predict_proba(temp).tolist()
		self.Y_test_pred = temp["y_pred"]

		temp = self.X_train.copy()
		temp["y_pred"] = self.model.predict_proba(temp).tolist()
		self.Y_train_pred = temp["y_pred"]

	def set_train_test_data(self, t_size=0.2):

		data = self.encode()
		x, y = data[data.columns.difference(["Target"])], data["Target"]

		self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
			x, y, test_size=t_size, random_state=42)

	def decode_sf(self, slice_list):

		for s in slice_list:
			for k, v in list(s.slice_des.items()):
				if k in self.encoders:
					le = self.encoders[k]
					temp = []
					for v_ in v:
						temp.append(le.inverse_transform(v_)[0])
					if (len(temp) == 1):
						s.slice_des[k] = temp[0]
					else:
						s.slice_des[k] = temp
				else:
					for v_ in sorted(v, key=lambda x: x[0]):
						if len(v_) > 1:
							s.slice_des[k] = (v_[0], v_[1])
						else:
							s.slice_des[k] = (v_[0])

		return slice_list

	def extract_data(self, index_list, flag):

		x = self.X_test.copy()
		y = self.Y_test.copy()

		x = x[x.index.isin(index_list)]
		y = y[y.index.isin(index_list)]

		if flag:
			return x, y
		else:
			return x

	def drill_down(data, slice_def):

		a = data.copy

		for k, v in slice_def.items():
			a = a.loc[a[k].isin([v])]

		return a

	def violin_data(self, index, tick=0.01, max_r=10):

		x, y = self.extract_data(index, flag=True)

		count = [0] * (int((max_r/tick)) + 1)

		div = len(count)

		h = self.model.predict_proba(x)[:, 1]

		loss = (-y * np.log(h) - (1 - y) * np.log(1 - h))

		loss = (loss/max(loss)) * max_r

		for i in loss:
			count[int(i/tick)] += 1

		x = [round(i/div, 4) for i in range(div)]

		temp = list(zip(x, count))
		violin_data = pd.DataFrame(temp, columns=['x', 'y'])

		return json.loads(violin_data.to_json(orient='records'))
		# return list(zip(x, count))

	def conf_mat(self, index_list):

		x = self.X_test.copy()
		y = self.Y_test.copy()

		x = x[x.index.isin(index_list)]
		y_t = y[y.index.isin(index_list)]

		y_p = self.model.predict(x)

		print(y_t,y_p)

		tn, fp, fn, tp = confusion_matrix(y_t, y_p).ravel()

		p = tp + fn
		n = fp + tn

		accuracy = round((tp+tn)/(p+n), 3)
		f1 = round(2*tp/(2*tp+fp+fn), 3)
		precision = round(tp/(tp+fp), 3)
		recall = round(tp/(tp+fn), 3)

		temp = {"accuracy": accuracy,
				"f1": f1,
				"precision": precision,
				"recall": recall,
				"tp": tp,
				"fp": fp,
				"fn": fn,
				"tn": tn
				}
		return temp


if __name__ == "__main__":
	obj = datahandler("./data/adult.csv", ["Target"])
	var = obj.encode()
	X_train, X_test, y_train, y_test = obj.test_train_data()
	# print(var)
	print(X_train, X_test, y_train, y_test)
