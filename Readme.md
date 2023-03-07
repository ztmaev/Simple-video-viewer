<h1>Simple video viewer</h1>
<li>Lists your videos</li>
<li>Plays your videos</li>
<li>Search functionality</li>
<li>Generates thumbnails and duration for fast startup</li>
<li>Move functionality to move media you don't want in the directory</li>
<h2>Requirements</h2>
Flask==2.2.2 flask_paginate==2022.1.8
moviepy==1.0.3
Pillow==9.4.0
<li>Flask</li>
<li>Flask_paginate</li>
<li>Moviepy</li>
<li>Pillow</li>
<h2>Setup</h2>
1. <strong>Edit config.json</strong> <br>


>  <strong>host-address</strong> : "The full host adress" <br> eg: http://localhost:5500/  or https://example.example.com/ for external connections<br>
>  <strong>port</strong> : Port ur using, forwarded for external connections <br>
>  <strong>title</strong> : "server title"

2. <strong>Commands</strong> <br>

> pip install -r requirements.txt <br>
> python3 main.py

<h3>Usage</h3>
<li>Go to the host adress and port you set in config.json</li>
<li>To move a video to the move directory, click the '⤴️' button on the thumbnails</li>

<h3>Note</h3>
<li>1st time startup will take a while to generate thumbnails and duration for all videos in the directory.
<li>Corrupted videos are moved to the 'move_path' in the config.json file</li>
<li>Make sure you have ffmpeg installed on your system</li>