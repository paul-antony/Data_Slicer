
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename


from src.Data_handler.datahandler import Datahandler
from src.data_slicer.slice_finder import Slice, SliceFinder
from src.model_selector import model_select
from src.sf_main import run_slice_finder
from src.pl_main import run_palm


UPLOAD_FOLDER = './upload'

if os.path.exists(UPLOAD_FOLDER) == False:
	os.mkdir(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, static_folder="static")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

global_data = {"flag" : False}


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
							   filename)


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():

	global global_data

	if request.method == 'POST':
		# check if the post request has the file part

		file = request.files['file']

		if file and allowed_file(file.filename):
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'))
			k = int(request.form['K'])
			ml_model = int(request.form['ML-Model'])
			global_data['file_name'] = file.filename
			global_data['K'] = k
			global_data['model_id'] = ml_model
			# print(k,ml_model)
			return redirect(url_for('load'))

	global_data = {"flag" : False}
	return render_template("index.html")


@app.route('/dash')
def load():
	model = model_select(global_data['model_id'])
	data_obj = Datahandler("upload/data.csv", model)
	print(data_obj.target_types,type(data_obj.target_types),data_obj.target_types[0],data_obj.target_types[1])

	global_data['data_obj'] = data_obj

	return render_template("load.html")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

	global global_data

	data_obj = global_data['data_obj']
	K = global_data['K']

	if (global_data["flag"] == False):
		recommendations = run_slice_finder(data_obj, K=K)
		global_data['recommendations'] = recommendations
		palm_data = run_palm(K,data_obj)
		global_data['palm'] = palm_data
		global_data["flag"] = True

	op_para = {}
	op_para['K'] = global_data['K']
	recommendations = global_data['recommendations']

	v_data = []
	slice_des = []

	for i in recommendations:
		v_data.append(data_obj.violin_data(i.slice_index, tick=0.1))
		slice_des.append(i.discript_html())

	op_para["slice_des"] = slice_des
	op_para['v_data'] = v_data
	op_para['palm'] = global_data['palm']
	return render_template("dashboard.html", op_para=op_para)


@app.route('/dashboard/<int:slice_id>', methods=['GET', 'POST'])
def detail(slice_id):

	global global_data
	data_obj = global_data['data_obj']
	K = global_data['K']
	recommendations = global_data['recommendations']

	if request.method == 'POST':
		pass

	else:

		slice_detail = recommendations[slice_id]

		op_para = {}
		op_para["slice_des"] = slice_detail.discript_html()
		op_para['v_data']=data_obj.violin_data(slice_detail.slice_index, tick = 0.1)

		op_para["cmatrix"] = data_obj.conf_mat(slice_detail.slice_index)
		op_para["class"] = [data_obj.target_types[0],data_obj.target_types[1]]

		return render_template("detail.html", op_para=op_para)






if __name__ == '__main__':
	app.run(debug = True)
