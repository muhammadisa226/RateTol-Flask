from flask import Flask, make_response, jsonify, render_template
from flask_restx import Resource, Api, reqparse
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import  CORS
from werkzeug.datastructures import FileStorage
import numpy as np
from keras.models import load_model
from keras_preprocessing import image
import chatbot



app = Flask(__name__)
app.config.SWAGGER_UI_OAUTH_APP_NAME = 'Rate Tol | Api '
api = Api(app,title=app.config.SWAGGER_UI_OAUTH_APP_NAME)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
db = SQLAlchemy()
db.init_app(app)

# inisialisai model tabel image
class ImagesModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False)
    tujuan = db.Column(db.String, nullable=False)

# Create Database:
with app.app_context():
    db.create_all()



@api.route('/image/all')
class ImageAll(Resource):
    def get(self):
        images = ImagesModel.query.all()
        data = [
            {
                "id": data.id,
                "name": data.name,
                "created_at": data.created_at,
                "tujuan": data.tujuan,
            }
            for data in images
        ]
        return data
        

uploadParser = api.parser()
uploadParser.add_argument('image', location='files', type=FileStorage, required=True)
uploadParser.add_argument('tujuan', type=str, help='[Semarang,Solo,Brebes Timur, Brebes Barat]', location='form')
@api.route('/image/upload')
class ImageApi(Resource):
    @api.expect(uploadParser)
    def post(self):
        args = uploadParser.parse_args()
        file = args['image']
        file.save("./images_upload/" + file.filename)
        filename = file.filename
        created_at = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        tujuan = args['tujuan']
        imagedb = ImagesModel(name=filename, created_at=created_at,tujuan=tujuan)
        db.session.add(imagedb)
        db.session.commit()
        #AI CODE
        model = load_model('modelkendaraan.h5')
        path = "./images_upload/" + filename
        img = image.load_img(path, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        array = model.predict(x)
        result = array[0]
        answer = np.argmax(result)
        if answer == 0 and tujuan == 'Semarang':
            return jsonify({"message":{
                'jenis_kendaraan' : 'Bus',
                'tarif' : 'Rp. 129.000',
                'tujuan' : 'Semarang'
            }})
        elif answer == 0 and tujuan == 'Solo':
            return jsonify({"message": {
                'jenis_kendaraan': 'Bus',
                'tarif': 'Rp. 85.000',
                'tujuan': 'Solo'
            }})
        elif answer == 0 and tujuan == 'Brebes Timur':
            return jsonify({"message": {
                'jenis_kendaraan': 'Bus',
                'tarif': 'Rp. 16.500',
                'tujuan': 'Brebes Timur'
            }})
        elif answer == 0 and tujuan == 'Brebes Barat':
            return jsonify({"message": {
                'jenis_kendaraan': 'Bus',
                'tarif': 'Rp. 26.000',
                'tujuan': 'Brebes Barat'
            }})
        elif answer == 1 and tujuan == 'Semarang':
            return jsonify({"message":{
                'jenis_kendaraan' : 'Mobil',
                'tarif' : 'Rp. 86.000',
                'tujuan': 'Semarang'
            }})
        elif answer == 1 and tujuan == 'Solo':
            return jsonify({"message": {
                'jenis_kendaraan': 'Mobil',
                'tarif': 'Rp. 56.500 ',
                'tujuan': 'Solo'
            }})
        elif answer == 1 and tujuan == 'Brebes Timur':
            return jsonify({"message": {
                'jenis_kendaraan': 'Mobil',
                'tarif': 'Rp. 11.000',
                'tujuan': 'Brebes Timur'
            }})
        elif answer == 1 and tujuan == 'Brebes Barat':
            return jsonify({"message": {
                'jenis_kendaraan': 'Mobil',
                'tarif': 'Rp. 17.500',
                'tujuan': 'Brebes Barat'
            }})
        elif answer == 2 and tujuan == 'Semarang':
            return jsonify({"message":{
                'jenis_kendaraan': 'Truk',
                'tarif' : 'Rp. 172.000',
                'tujuan': 'Semarang'
            }})
        elif answer == 2 and tujuan == 'Solo':
            return jsonify({"message":{
                'jenis_kendaraan': 'Truk',
                'tarif' : 'Rp. 113.500',
                'tujuan': 'Solo'
            }})
        elif answer == 2 and tujuan == 'Brebes Timur':
            return jsonify({"message":{
                'jenis_kendaraan': 'Truk',
                'tarif' : 'Rp. 22.000',
                'tujuan': 'Brebes Timur'
            }})
        elif answer == 2 and tujuan == 'Brebes Barat':
            return jsonify({"message":{
                'jenis_kendaraan': 'Truk',
                'tarif' : 'Rp. 34.500',
                'tujuan': 'Brebes Barat'
            }})

loginParser = reqparse.RequestParser()
loginParser.add_argument('username', type=str, help='Username', location='form')
loginParser.add_argument('password', type=str, help='Password', location='form')
@api.route('/login')
class LoginUser(Resource):
    @api.expect(loginParser)
    def post(self):
        args = loginParser.parse_args()
        username = args['username']
        password = args['password']

        if username == 'admin' and password == 'admin':
            return make_response(jsonify({'data' : {
                'username': username
            },'message': "Login Sukses",
              'status_code': 200}),200)
        else:
            return make_response(jsonify({'message' : "Login Gagal",}), 400)

chatbotParser = reqparse.RequestParser()
chatbotParser.add_argument('msg', type=str, help='Message', location='args')
@api.route('/getchatbot')
class Chatbot(Resource):
    @api.expect(chatbotParser)
    def get(self):
        args = chatbotParser.parse_args()
        msg = args['msg']
        return chatbot.chatbot_response(msg)




@app.route('/home', methods=["GET","POST"])
def home():
    title = 'Rate Tol | Home'
    return  render_template('index.html', title=title)

@app.route('/history', methods=["GET"])
def history():
    title = 'Rate Tol | History'
    return  render_template('history.html', title=title)

@app.route('/chatbot', methods=["GET"])
def chatbotgui():

    title = 'Rate Tol | Chatbot'
    return  render_template('chatbot.html', title=title)


if __name__ == '__main__':
    app.run(host='192.168.163.50', port=5000, debug=True)