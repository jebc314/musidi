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
import os, sys
import subprocess
import speech_recognition as sr
import wave

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/musidi',methods=['POST'])
def musidi():
    link = [x for x in request.form.values()]
    #name = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(10))
    name = 'song_file'

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

    os.replace(f'./output/{name}/vocals.wav', f'Audio-to-midi-master/input/{name}_vocals.wav')
    for x in os.walk('Audio-to-midi-master/input/'):
        print(x)
    print('running model')
    _output = subprocess.run([sys.executable, 'Audio-to-midi-master/audio2midi.py', '-in', 'Audio-to-midi-master/input/', '-out', 'Audio-to-midi-master/output/'])

    os.replace(f'Audio-to-midi-master/output/{name}_vocals.mid', f'./{name}_vocals.mid')
    print('moved output. can you see it?')

    '''
    f = open(f'{name}_lyrics.txt', 'w')
    # https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python
    r = sr.Recognizer()
    with sr.AudioFile(f'./Audio-to-midi-master/input/{name}_vocals.wav') as source:
        # listen for data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech/song to text)
        text = r.recognize_google(audio_data, language = 'en-IN', show_all=True) # may only work for files less than ~110 seconds long, need to split otherwise
        f.write(str(text))
    f.close()
    '''
    print('printed lyrics to txt. can you see it?')
    from roll import MidiFile
    mid = MidiFile(name+'_vocals.mid')
    mid.draw_roll()
    return render_template('index.html', output='{}/other.wav'.format(name), picture=name+'_vocals.png', youtube=link[0][-11:])

@app.route('/musidi/output/<path:filename>')
def download_file(filename):
    print(filename)
    return send_file('output/'+filename)

@app.route('/musidi/<path:filename>')
def download_image(filename):
    print(filename)
    return send_file(filename)

if __name__ == "__main__":
    app.run(debug=True)

