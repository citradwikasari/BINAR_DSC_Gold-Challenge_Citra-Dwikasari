#membuat endpoint dari API yang dapat menginput teks via form dan file CSV

from flask import Flask, request, jsonify
import pandas as pd
import re
import string

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)

"""Review: Taruh load data disini, setelah load library yang dibutuhin"""
dict1 = pd.read_csv('abusive.csv', encoding='latin-1') #read data abusive.

dict2 = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None) #data "alay dictionary"
dict2 = dict2.rename(columns={0: 'original', 
                                      1: 'replacement'}) 

#Template swagger
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
# End template swagger

"""Review:
ini perbaiki yah. sebaiknya ditaruh diatas setelah load library, jangan di tengah2 code. Khawatirnya sulit di trace kalau mau update data"""
## membaca file kamus pertama
# dict1 = pd.read_csv('abusive.csv')

# # membaca file kamus kedua
# dict2 = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
# dict2 = dict2.rename(columns={0: 'original', 
#                                       1: 'replacement'})


# Inisialisasi setiap fungsi cleansing pakai konsep Object Oriented Programming biar mudah dibaca sama data scientist lain / programmer
# Inisialisasi fungsi
# rules 1: menghilangkan karakter non-alfanumerik dan membuat semua huruf kecil
def lowercase(text):
    return text.lower()

# rules 2:
"""Disini masih ada eror: bisa liat referensi cleansing nya di: 
https://www.kaggle.com/code/ilhamfp31/preprocessing-the-indonesian-hate-abusive-text
Terlampir contoh eror dari proses cleansing disini ada di file 'eror fungsi regex.PNG'
"""

def remove_unnecessary_char(text):
    # menghilangkan URLs, RT, user and mentions
    text = re.sub(r"http\S+|rt|user|@\S+", "", text)
    # memisahkan kata yang mengandung punctuation atau tanda baca
    text = re.findall(r'\w+', text)
     # menghapus single character
    text = re.sub(r'\s+\w{1}\s+', ' ', text)
    # menghilangkan tanda baca 
    text = re.sub(r'[^\w\s]', '', text)
    # menghilangkan digits
    text = re.sub('\d+', '',text)
    # menghapus karakter selain huruf, angka, dan spasi
    text = re.sub(r'[^\w\s]', '', text)
    # menghapus angka
    text = re.sub(r'\d+', '', text)
    return text

# rules 5 : mengganti kata-kata yang ada di kamus pertama
def remove_abusive(text):
    text = ' '.join(['' if word in dict1.abusive.values else word for word in text.split(' ')])
    text = re.sub('  +', ' ', text) # Remove extra spaces
    text = text.strip()
    return text


# rules 4: mengganti kata-kata yang ada di kamus kedua
alay_dict_map = dict(zip(dict2['original'], dict2['replacement']))
def normalize_alay(text):
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])


# jadikan seluruh fungsi dalam 1 fungsi
def cleansing(text):
    text = lowercase(text) # rules 1
    text = remove_unnecessary_char(text) # rules 2
    text = remove_abusive(text) # rules 3
    text = normalize_alay(text) # rules 4
    return text
# end inisialisasi fungsi


# endpoint pengenalan aplikasi
@swag_from('docs/landingpage.yml', methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "DISINI KASIH JUDUL APLIKASI SESUAI REPORT",
        'data': "Binar Academy - Nama - DSC 7",
    }

    response_data = jsonify(json_response)
    return response_data

# endpoint untuk membersihkan teks dari file CSV
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/cleansing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    """Review: disini masukin fungsi yang udah di gabung yaitu fungsi def cleansing(text) di dalam response data"""
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        # 'data': re.sub(r'[^a-zA-Z0-9]', ' ', text),
        'data' : cleansing(text)
    }

    response_data = jsonify(json_response)
    return response_data

# endpoint untuk membersihkan teks dari input form
@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/cleansing-file', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file, encoding='latin-1')

    # Lakukan cleansing pada teks
    cleaned_text = []
    for text in df['Tweet']:
        """Review disini masukin fungsi yang udah di gabung yaitu fungsi def cleansing(text)"""
        # cleaned_text.append(re.sub(r'[^a-zA-Z0-9]', ' ', text))
        cleaned_text.append(cleansing(text))

    df['cleaned_text'] = cleaned_text

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run(debug=True)
