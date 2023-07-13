from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_cors import cross_origin

import random
import os
import csv
import time
import datetime
import subprocess
import time
import pathlib




app = Flask(__name__)
CORS(app, origins=["*"])

app.config['UPLOAD_FOLDER'] = 'csv_files/'

IMAGE_THEMES = {
    "image1": [
        "A: なんで？の「はぁ」",
        "B: 力をためる「はぁ」",
        "C: ぼうぜんの「はぁ」",
        "D: 感心の「はぁ」",
        "E: 怒りの「はぁ」",
        "F: とぼけの「はぁ」",
        "G: おどろきの「はぁ」",
        "H: 失恋の「はぁ」"
    ],
    "image2": [
        "A: 理解して「はぁ」",
        "B: いい加減な返事の「はぁ」",
        "C: やっちゃった!の「はぁ」",
        "D: おどして「はぁ」",
        "E: 演歌の「はぁ」",
        "F: 恐ろしくて「はぁ」",
        "G: バカにして「はぁ」",
        "H: 恋が実って「はぁ」"
    ],
    "image3": [
        "A: 憧れの人に出会って「はぁ」",
        "B: ゾンビから逃げ切って「はぁ」",
        "C: 必殺技を出す前の「はぁ」",
        "D: バカなことを言われて「はぁ」",
        "E: 電車に間に合って「はぁ」",
        "F: 温泉に入って「はぁ」",
        "G: オペラ風に「はぁ」",
        "H: 雪女が息を吐いて「はぁ」"
    ],
    "image4": [
        "A: 好きな人を思い出して「はぁ」",
        "B: 全財産を失った時の「はぁ」",
        "C: 熱いお風呂に入って「はぁ」",
        "D: 全力で戦いを終えて「はぁ」",
        "E: してない万引きを疑われて「はぁ」",
        "F: ヘロヘロになって「はぁ」",
        "G: 興奮してるのを隠して「はぁ」",
        "H: 失敗を悔やんで「はぁ」"
    ],
}

ALLOWED_EXTENSIONS = {'csv'}



def convert_webm_to_mp4(webm_path, mp4_path):
    command = f'ffmpeg -i {webm_path} -vcodec h264 -pix_fmt yuv420p -movflags faststart {mp4_path}'
    subprocess.run(command, shell=True, check=True)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/get_theme')
@cross_origin(origins=["http://ccca-lab.net"])
def get_theme():
    image_id = request.args.get('image_id', type=str)
    image_id = "image" + image_id
    if image_id in IMAGE_THEMES:
        theme = random.choice(IMAGE_THEMES[image_id])
        return jsonify({'theme': theme})
    else:
        return jsonify({'error': 'Invalid image id.'}), 400


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_vote_choices')
@cross_origin(origins=["http://ccca-lab.net"])
def get_vote_choices():
    image_id = request.args.get('image_id', type=str)
    image_id = "image" + image_id
    if image_id in IMAGE_THEMES:
        return jsonify({'choices': IMAGE_THEMES[image_id] + ['I: 自分の番です']})
    else:
        return jsonify({'error': 'Invalid image id.'}), 400


@app.route('/api/submit_vote', methods=['POST'])
def submit_vote():
    if request.content_type.startswith('multipart/form-data'):
        data = {}
        for i in range(1, 9):
            vote_chip = request.form.get("vote_chip_" + str(i))
            if vote_chip and len(vote_chip) > 0:
                # 先頭のアルファベットのみを抽出
                vote_chip = vote_chip[0]
            data["vote_chip_" + str(i)] = vote_chip

        # ユーザー名、実行回数を取得
        username = data["username"] = request.form.get("username")
        if not username:
            return 'Missing username', 400

        participation_count = data["participation_count"] = request.form.get("participation_count")
        if not participation_count:
            return 'Missing participation count', 400

        # 演技のアルファベットを取得、先頭のアルファベットのみを抽出
        your_situation = request.form.get("theme")
        if your_situation and len(your_situation) > 0:
            your_situation = your_situation[0]
        data["theme"] = your_situation

        if not your_situation:
            return 'Missing theme', 400

        # 画像IDを取得
        image_id = request.form.get("image_id")
        print("Image ID: ", image_id)
        if not image_id:
            return 'Missing image id', 400

        # ビデオデータの取得と保存

        video_data = request.files.get("video")
        if video_data:
            video_filename = f'{image_id}_{username}_{participation_count}_{your_situation}_{datetime.datetime.now().timestamp()}'
            video_extension = pathlib.Path(video_data.filename).suffix
            video_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video_filename + video_extension))
            video_data.save(video_filepath)

            # If video is in .webm format, convert to .mp4
            if video_extension == '.webm':
                mp4_filename = video_filename + '.mp4'
                mp4_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(mp4_filename))
                convert_webm_to_mp4(video_filepath, mp4_filepath)
                os.remove(video_filepath)  # Remove the original .webm file
                video_filepath = mp4_filepath

        csv_filename = f'{image_id}_{username}_{participation_count}_{your_situation}_{datetime.datetime.now().timestamp()}.csv'
        csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(csv_filename))

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'participation_count', 'theme',
                          'vote_chip_1', 'vote_chip_2', 'vote_chip_3', 'vote_chip_4',
                          'vote_chip_5', 'vote_chip_6', 'vote_chip_7', 'vote_chip_8']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow(data)

        return 'OK'
    else:
        return 'Content-type must be multipart/form-data.'

@app.route('/list_csv')
def list_csv():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            files.append(filename)
    return render_template('list_csv.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    directory = app.config['UPLOAD_FOLDER']
    return send_from_directory(directory, filename, as_attachment=True)



@app.route('/api/get_self_choice')
@cross_origin(origins=["http://ccca-lab.net"])
def get_self_choice():
    image_id = request.args.get('image_id', type=str)
    image_id = "image" + image_id
    if image_id in IMAGE_THEMES:
        return jsonify({'choices': IMAGE_THEMES[image_id]})
    else:
        return jsonify({'error': 'Invalid image id.'}), 400

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400
