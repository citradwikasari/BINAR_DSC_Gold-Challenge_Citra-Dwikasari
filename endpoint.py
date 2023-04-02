#membuat endpoint dari API yang dapat menginput teks via form dan file CSV

from flask import Flask, request, jsonify
import pandas as pd
import re
import string

app = Flask(__name__)



#bikin template swagger
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
    
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

# membaca file kamus pertama
dict1 = pd.read_csv('abusive.csv')

# membaca file kamus kedua
dict2 = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
dict2 = dict2.rename(columns={0: 'original', 
                                      1: 'replacement'})

# endpoint untuk membersihkan teks dari file CSV
@app.route('/text-processing-file.yml', methods=['POST'])
@app.route('/cleansing', methods=['POST']) 
def cleansing_from_csv():
    # membaca file CSV
    file = request.files['file']
    data = pd.read_csv(file, encoding='latin-1')

    # memberi nama kolom teks
    data.columns = ['teks']

    # menghilangkan karakter non-alfanumerik dan membuat semua huruf kecil
    data['teks'] = data['teks'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x).lower())

    # menghilangkan URLs, RT, user and mentions
    data['teks'] = data['teks'].apply(lambda x: re.sub(r"http\S+|rt|user|@\S+", "", x))

    # memisahkan kata yang mengandung punctuation atau tanda baca
    data['teks'] = data['teks'].apply(lambda x: ' '.join(re.findall(r'\w+', x)))

    # menghapus single character
    data['teks'] = data['teks'].apply(lambda x: re.sub(r'\s+\w{1}\s+', ' ', x))

    # menghilangkan tanda baca 
    data['teks'] = data['teks'].apply(lambda x: re.sub(r'[^\w\s]', '', x))

    # menghilangkan digits
    data['teks'] = data['teks'].apply(lambda x: re.sub('\d+', '',x))

    # menghapus karakter selain huruf, angka, dan spasi
    data['teks'] = data['teks'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    
    # menghapus angka
    data['teks'] = data['teks'].apply(lambda x: re.sub(r'\d+', '', x))

    # mengganti kata-kata yang ada di kamus pertama
    data['teks'] = data['teks'].apply(lambda x: ' '.join([dict1.get(word, word) for word in x.split()]))
    
    # mengganti kata-kata yang ada di kamus kedua
    data['teks'] = data['teks'].apply(lambda x: ' '.join([dict2.get(word, word) for word in x.split()]))

    # menghapus spasi berlebih
    data['teks'] = data['teks'].apply(lambda x: re.sub('\s+', ' ', x))

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', data),
    }

    # menyimpan hasil cleansing ke dalam file baru
    result_file = 'cleaned_data.csv'
    data.to_csv(result_file, index=False)

    response_data = jsonify(json_response)
    return response_data

    #return jsonify({'status': 'success', 'message': 'Data berhasil dibersihkan dan disimpan di file ' + result_file})

# endpoint untuk membersihkan teks dari input form
@app.route('/text-processing.yml', methods=['POST'])
@app.route('/cleansing/form', methods=['POST'])
def cleansing_from_form():
    teks = request.form.get('teks')

    # menghilangkan karakter non-alfanumerik dan membuat semua huruf kecil
    teks = re.sub(r'[^a-zA-Z0-9\s]', '', teks).lower()
    
    # menghilangkan URLs, RT, user and mentions
    teks = teks.apply(lambda x: re.sub(r"http\S+|rt|user|@\S+", "", x))

    # memisahkan kata yang mengandung punctuation atau tanda baca
    teks = teks.apply(lambda x: ' '.join(re.findall(r'\w+', x)))

    # menghapus single character
    teks = teks.apply(lambda x: re.sub(r'\s+\w{1}\s+', ' ', x))

    # menghilangkan tanda baca 
    teks = teks.apply(lambda x: re.sub(r'[^\w\s]', '', x))

    # menghilangkan digits
    teks = teks.apply(lambda x: re.sub('\d+', '',x))

    # menghapus karakter selain huruf, angka, dan spasi
    teks = teks.apply(lambda x: re.sub(r'[^\w\s]', '', x))
    
    # menghapus angka
    teks = teks.apply(lambda x: re.sub(r'\d+', '', x))

    # mengganti kata-kata yang ada di kamus pertama
    teks = teks.apply(lambda x: ' '.join([dict1.get(word, word) for word in x.split()]))
    
    # mengganti kata-kata yang ada di kamus kedua
    teks = teks.apply(lambda x: ' '.join([dict2.get(word, word) for word in x.split()]))

    # menghapus spasi berlebih
    teks = teks.apply(lambda x: re.sub('\s+', ' ', x))

    # menggabungkan kembali list of words menjadi teks baru
    teks = ' '.join(teks)

    #return jsonify({'status': 'success', 'teks': teks})
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', teks),
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run(debug=True)
