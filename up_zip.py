from flask import Flask, request, render_template, redirect,flash,session
import os
import configparser
import re
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置 Flask 的密钥，用于 flash 消息
# 设置上传文件的保存目录（可以自定义）
config = configparser.ConfigParser()
config.read('config.ini')
UPLOAD_FOLDER = config['DEFAULT']['UPLOAD_FOLDER']  # 默认保存到项目根目录下的 uploads 文件夹
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'zip'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 首页路由，用于上传文件
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # 如果用户没有选择文件
        if file.filename == '':
            flash('未选择文件')
            return redirect(request.url)
        # 如果文件不是 ZIP 类型
        if not allowed_file(file.filename):
            flash('只允许上传 ZIP 类型的文件')
            return redirect(request.url)
        # 获取 license 有效期
        license = request.form.get('license')
        # 简单验证 license 格式（可根据需求进一步完善）
        if not re.match(r'^\d{8}-\d{8}$', license):
            flash('请输入正确的 license 有效期格式：8 位年月日格式-8 位年月日格式')
            return redirect(request.url)
        # 如果文件合法且是 ZIP 文件
        if file and allowed_file(file.filename):
            # 保存文件到指定目录
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            # 存储 license 到会话中
            session['license'] = license
            flash(f"文件上传成功！保存路径：{file_path}")
            return redirect(request.url)

    return render_template('upload.html')
# 查询路由
@app.route('/query')
def query():
    license_info = session.get('license', '未找到 license 信息')
    return render_template('query_date.html', license_info=license_info)
if __name__ == '__main__':
    app.run(debug=True)