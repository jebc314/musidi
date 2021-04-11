#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
from flask import Flask,render_template,request,send_file
from spleeter import separator
import youtube_dl
import random
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/musidi',methods=['POST'])
def musidi():
    link = [x for x in request.form.values()]
    name = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(10))
    #name = 'song_file'

    local_file_path = name + ".mp3"
    ydl_args = {
        'format': 'bestaudio/best',
        'outtmpl': local_file_path
    }

    ydl = youtube_dl.YoutubeDL(ydl_args)
    ydl.download([link[0]]) 

    separator = Separator('4stems.json', multiprocess=False)

    audio_loader = AudioAdapter.default()
    sample_rate = 44100
    waveform, _ = audio_loader.load(local_file_path, sample_rate=sample_rate, duration=60)
    separator.separate_to_file(local_file_path, 'output/', audio_adapter=audio_loader)

    return render_template('index.html', output='{}/other.wav'.format(name))

@app.route('/musidi/output/<path:filename>')
def download_file(filename):
    print(filename)
    return send_file('output/'+filename)

if __name__ == "__main__":
    app.run(debug=True)

