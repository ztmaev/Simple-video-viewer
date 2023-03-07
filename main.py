import json
import os
import random
from PIL import Image
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from moviepy.video.io.VideoFileClip import VideoFileClip
import shutil

with open('config.json', 'r') as f:
    config = json.load(f)

    hosted = config['host-address']
    port = config['port']
    title = config['title']

    videos_path = config['videos_path']
    json_path = config['json_path']
    errors_path = config['errors_path']
    move_path = config['move_path']
    thumbnails_path = config['thumbnails_path']

app = Flask(__name__)

with open(json_path, 'r') as f:
    duration_data = json.load(f)


class VideoClipException(Exception):
    """Exception raised for video clip related errors."""

    def __init__(self, message):
        self.message = message


@app.route('/media')
def media():
    directory = os.path.abspath(os.getcwd())

    files = os.listdir(directory)

    file_links = ''
    for f in files:
        file_links += f'<li><a href="{f}">{f}</a></li>'

    return f'<html><body><ul>{file_links}</ul></body></html>'


@app.route('/media/<path:filename>')
def serve_file(filename):
    filepath = os.path.abspath(os.path.join(os.getcwd(), filename))

    if not os.path.exists(filepath):
        return "File not found", 404

    if os.path.isdir(filepath):
        files = os.listdir(filepath)
        file_links = ''
        for f in files:
            file_links += f'<li><a href="{filename}/{f}">{f}</a></li>'
        return f'<html><body><ul>{file_links}</ul></body></html>'

    return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath))


@app.route('/')
def index():
    videos = [f for f in os.listdir(videos_path) if os.path.isfile(os.path.join(videos_path, f)) and (
                f.endswith('.mp4') or f.endswith('.ts') or f.endswith('.mov') or f.endswith('.mkv'))]
    durations = {}
    for video_file in videos:
        if video_file in duration_data:
            durations[video_file] = duration_data[video_file]
        else:
            try:
                video_path = os.path.join(videos_path, video_file)
                with VideoFileClip(video_path) as video:
                    duration = int(video.duration)
                    duration_string = f"{duration // 60}:{duration % 60:02d}"
                    durations[video_file] = duration_string

                    duration_data[video_file] = duration_string
                    with open(json_path, 'w') as f:
                        json.dump(duration_data, f)

                    thumbnail_time = duration // 2
                    thumbnail_filename = f"{os.path.splitext(video_file)[0]}.jpg"
                    thumbnail_path = os.path.join(thumbnails_path, thumbnail_filename)
                    thumbnail_frame = video.get_frame(thumbnail_time)
                    thumbnail_image = Image.fromarray(thumbnail_frame)
                    thumbnail_image.save(thumbnail_path)
                    print(f"Saved thumbnail for {video_file} ({duration} s)")

            except (OSError, ValueError, VideoClipException) as e:

                print(f"Error processing {video_file}: {e}")
                shutil.move(os.path.join(videos_path, video_file), os.path.join(errors_path, video_file))

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 50
    offset = (page - 1) * per_page
    pagination_videos = videos[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(videos), css_framework='bootstrap4')

    return render_template('index.html', videos=pagination_videos, videos_path=videos_path, durations=durations,
                           pagination=pagination, hosted=hosted, title=title, page=page)


@app.route('/video/<video_file>')
def video(video_file):
    video_name = os.path.splitext(video_file)[0]

    videos = [f for f in os.listdir(videos_path) if os.path.isfile(os.path.join(videos_path, f)) and (
                f.endswith('.mp4') or f.endswith('.ts') or f.endswith('.mov') or f.endswith('.mkv'))]

    durations = {}
    for video_file in videos:
        if video_file in duration_data:
            durations[video_file] = duration_data[video_file]
        else:
            video_path = os.path.join(videos_path, video_file)
            if video_file.endswith('.mp4') or video_file.endswith('.mov'):
                with VideoFileClip(video_path) as video:
                    duration = int(video.duration)
                    duration_string = f"{duration // 60}:{duration % 60:02d}"
            elif video_file.endswith('.ts') or video_file.endswith('.mkv'):
                with VideoFileClip(video_path, audio=False) as video:
                    duration = int(video.duration)
                    duration_string = f"{duration // 60}:{duration % 60:02d}"
            durations[video_file] = duration_string

            duration_data[video_file] = duration_string
            with open(json_path, 'w') as f:
                json.dump(duration_data, f)
            thumbnail_time = duration // 2
            thumbnail_filename = f"{os.path.splitext(video_file)[0]}.jpg"
            thumbnail_path = os.path.join(thumbnails_path, thumbnail_filename)
            with VideoFileClip(video_path) as video:
                thumbnail_frame = video.get_frame(thumbnail_time)
                thumbnail_image = Image.fromarray(thumbnail_frame)
                thumbnail_image.save(thumbnail_path)
                print(f"Saved for {video_file} ({duration} s)")

        page = request.args.get(get_page_parameter(), type=int, default=1)

    if len(videos) > 3:
        recommendations = random.sample(videos, 3)
    else:
        recommendations = random.sample(videos, len(videos))

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 50
    offset = (page - 1) * per_page
    pagination_videos = videos[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(videos), css_framework='bootstrap4')
    return render_template('video.html', video_name=video_name, videos_path=videos_path, videos=pagination_videos,
                           pagination=pagination, durations=durations, recommendations=recommendations, hosted=hosted,
                           title=title, page=page)


@app.route('/mv/<video_file>')
def move(video_file):
    shutil.move(os.path.join(videos_path, video_file), os.path.join(move_path, video_file))
    page_num = request.args.get('page', default=1, type=int)
    return redirect(url_for('index', page=page_num))


@app.route('/search')
def search():
    query = request.args.get('query', '').lower()  

    videos = [f for f in os.listdir(videos_path) if os.path.isfile(
        os.path.join(videos_path, f)) and query in f.lower()]  

    if not videos:
        return render_template('search.html', query=query, hosted=hosted, title=title, durations={}, results=0,
                               pagination=None, videos=[], page=1)

    durations = {}
    for video_file in videos:
        duration_string = ""
        if video_file in duration_data:
            durations[video_file] = duration_data[video_file]
        else:
            video_path = os.path.join(videos_path, video_file)
            if video_file.endswith('.mp4') or video_file.endswith('.mov'):
                with VideoFileClip(video_path) as video:
                    duration = int(video.duration)
                    duration_string = f"{duration // 60}:{duration % 60:02d}"
            elif video_file.endswith('.ts') or video_file.endswith('.mkv'):
                with VideoFileClip(video_path, audio=False) as video:
                    duration = int(video.duration)
                    duration_string = f"{duration // 60}:{duration % 60:02d}"
            durations[video_file] = duration_string

            duration_data[video_file] = duration_string
            with open(json_path, 'w') as f:
                json.dump(duration_data, f)

            thumbnail_time = duration // 2
            thumbnail_filename = f"{os.path.splitext(video_file)[0]}.jpg"
            thumbnail_path = os.path.join(thumbnails_path, thumbnail_filename)
            with VideoFileClip(video_path) as video:
                thumbnail_frame = video.get_frame(thumbnail_time)
                thumbnail_image = Image.fromarray(thumbnail_frame)
                thumbnail_image.save(thumbnail_path)
                print(f"Saved for {video_file} ({duration} s)")
    results = len(videos)
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 50
    offset = (page - 1) * per_page
    pagination_videos = videos[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(videos), css_framework='bootstrap4')
    return render_template('search.html', query=query, hosted=hosted, title=title, durations=durations, results=results,
                           pagination=pagination, videos=pagination_videos, page=page)


if __name__ == '__main__':
    app.run(port=port)
