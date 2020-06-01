import os, datetime, base64
from flask import Flask, flash, request, redirect, url_for, send_from_directory, json, jsonify
from werkzeug.utils import secure_filename
from diffimg import diff

UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'obj'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_BASE64 = './base64'
app.config['UPLOAD_BASE64'] = UPLOAD_BASE64

filenamebase = 'img'
index = 1

# 检查文件格式
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 获取文件扩展名
def file_extension(path): 
    return os.path.splitext(path)[1]

# 文件上传日志记录
def write_upload_log(filename):
    t = datetime.datetime.now()
    t_str = datetime.datetime.strftime(t,'%Y-%m-%d %H:%M:%S')
    with open('log.txt','a+') as f:
        f.write('['+t_str+']:'+filename+' upload.\n')

# 文件比较日志记录
def write_diff_log(result):
    t = datetime.datetime.now()
    t_str = datetime.datetime.strftime(t,'%Y-%m-%d %H:%M:%S')
    with open('log.txt','a+') as f:
        f.writelines('['+t_str+']:'+'Similarity：'+str((1-result)*100)+'%.\n')

def run_diff():
    # 计算相似率
    res = diff('./files/img1.png','./files/img2.png')
    # 写入日志
    write_diff_log(res)
    # 删除文件
    del_file('files')
    return res

def run_diff_base64():
    # 计算相似率
    res = diff('./base64/img1.png','./base64/img2.png')
    # 写入日志
    write_diff_log(res)
    # 删除文件
    del_file('base64')
    return res

# 递归删除目录下的图片及子目录
def del_file(path_data):
    for i in os.listdir(path_data) :# os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "/" + i#当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:#os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)

@app.route('/upload/img', methods=['GET', 'POST'])
def upload_img_file():
    if request.method == 'POST':
        # print('收到文物上传的post请求')
        # check if the post request has the file part
        if 'file' not in request.files:
            # print('No file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # print('No selected file')
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global index # 函数内使用全局变量需要声明一下
            filename = secure_filename(file.filename)
            # print('filename: ', filename)
            write_upload_log(filename)
            filename = (filenamebase + str(index) + file_extension(filename))
            # print('filename: ', filename)
            index = index + 1
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if index == 3:
            res = run_diff()
            index = 1
            # 返回json数据
            return jsonify({'diffResult':1-res})
        return 'need more file'
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

def save_base64_to_file(filename, imageData):
    file = open(app.config['UPLOAD_BASE64'] + '/' + filename, 'wb')
    file.write(imageData)
    file.close()


@app.route('/upload/base64', methods=['GET', 'POST'])
def upload_base64():
    if request.method == 'POST':
        # 检查
        # print(request.form)
        base641Data = request.form.get('base641')
        base642Data = request.form.get('base642')

        image1Data = base64.b64decode(base641Data)
        filename1 = (filenamebase + str(1) + '.png')
        write_upload_log(filename1)
        # 写入文件
        save_base64_to_file(filename1, image1Data)

        image2Data = base64.b64decode(base642Data)
        filename2 = (filenamebase + str(2) + '.png')
        write_upload_log(filename2)
        # 写入文件
        save_base64_to_file(filename2, image2Data)

        # 进行图片相思度比较
        res = run_diff_base64()
        # 返回json数据
        return jsonify({'diffResult':1-res})
    return '''
        need more base64 data
        '''


@app.route('/upload/obj', methods=['GET', 'POST'])
def upload_obj_file():
    if request.method == 'POST':
        # print('收到文物上传的post请求')
        # check if the post request has the file part
        if 'file' not in request.files:
            # print('No file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # print('No selected file')
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # print('filename: ', filename)
            write_upload_log(filename)
            filename = ('tempObj' + file_extension(filename))
            # print('filename: ', filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        return '临时Obj文件上传完毕，adress:5000/uploads/tempObj.obj 可以下载'
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)