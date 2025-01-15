import FreeSimpleGUI as sg
from flask import Flask, jsonify, render_template_string
import threading

# Define the levels and their corresponding point thresholds
LEVELS = [
    (5, ""),
    (10, ""),
    (15, ""),
    (25, ""),
    (30, ""),
    (40, ""),
    (50, ""),
    (60, ""),
    (75, ""),
    (90, ""),
    (100, ""),
    (120, ""),
    (150, ""),
    (180, ""),
    (200, ""),
    (400, ""),
    (500, ""),
    (750, ""),
    (900, ""),
    (1000, "")
]

# Initial setup
points = 0

# Flask setup
app = Flask(__name__)

# HTML template to be rendered
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress Bar</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            color: white;
            text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5);
        }
        h2, h3 {
            margin: 0;
        }
        .progress-container {
            position: relative;
            width: 80%;
            height: 40px;
            background-color: #f3f3f3;
            border-radius: 20px;
            margin: 20px auto;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .progress-bar {
            height: 100%;
            border-radius: 20px;
            background: linear-gradient(to right, #4caf50, #81c784);
            width: 0;
            transition: width 0.5s;
        }
        .progress-label {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            color: black;
            font-weight: bold;
            text-align: center;
            line-height: 40px;
            text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>
<body>
    <h2>Puntos: {{ points }}</h2>
    <div class="progress-container">
        <div class="progress-bar" style="width: {{ progress_percentage }}%;"></div>
        <div class="progress-label">{{ level }}</div>
    </div>
    <h3>Next Level: {{ next_level_points }} Points</h3>

    <script>
        function fetchProgress() {
            fetch('/progress')
                .then(response => response.json())
                .then(data => {
                    const progressBar = document.querySelector('.progress-bar');
                    const progressLabel = document.querySelector('.progress-label');
                    const pointsText = document.querySelector('h2');
                    const nextLevelText = document.querySelector('h3');

                    progressBar.style.width = data.progress_percentage + '%';
                    progressLabel.innerText = data.level;
                    pointsText.innerText = "Puntos: " + data.points;
                    nextLevelText.innerText = "Proximo nivel: " + data.next_level_points + " Puntos";
                });
        }

        setInterval(fetchProgress, 1000);
    </script>
</body>
</html>
"""

# Function to determine the current level, max points, and progress percentage for the level
def get_current_level(points):
    prev_threshold = 0
    for threshold, level_name in LEVELS:
        if points < threshold:
            max_points = threshold - prev_threshold
            progress = points - prev_threshold
            progress_percentage = (progress / max_points) * 100
            return level_name, max_points, progress, progress_percentage, threshold
        prev_threshold = threshold
    return "!", 1000 - prev_threshold, points - prev_threshold, 100, 1000  # Max level

# Flask route to serve the HTML template
@app.route('/')
def index():
    global points
    level, max_points, progress, progress_percentage, next_level_points = get_current_level(points)
    return render_template_string(html_template, points=points, level=level, progress_percentage=progress_percentage, next_level_points=next_level_points)

# Flask route to get the current progress as JSON
@app.route('/progress')
def get_progress():
    global points
    level, max_points, progress, progress_percentage, next_level_points = get_current_level(points)
    return jsonify({
        'points': points, 
        'level': level, 
        'progress_percentage': progress_percentage, 
        'next_level_points': next_level_points
    })

# Run Flask in a separate thread
def run_flask():
    app.run(debug=False, port=5000, use_reloader=False)

# Start the Flask server in a new thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# PySimpleGUI layout with custom input fields
layout = [
    [sg.Text(f'Puntos: {points}', key='-POINTS-')],
    [sg.Text(f'Nivel: {get_current_level(points)[0]}', key='-LEVEL-')],
    [sg.ProgressBar(get_current_level(points)[1], orientation='h', size=(20, 20), key='-PROG-')],
    [sg.Button('+1'), sg.Button('+2'), sg.Text('Puntos:'), sg.InputText(key='-ADD_CUSTOM-', size=(10, 1)), sg.Button('Añadir')],
    [sg.Button('-1'), sg.Button('-2'), sg.Text('Puntos:'), sg.InputText(key='-REMOVE_CUSTOM-', size=(10, 1)), sg.Button('Remover')],
    [sg.Button('Exit')]
]

# Create the window
window = sg.Window('Tracker extensible', layout)

# Function to update the points, progress bar, and level
def update_progress(change):
    global points
    points = max(0, min(1000, points + change))  # Limit points to 0-1000 range

    level, max_points, progress, progress_percentage, next_level_points = get_current_level(points)

    window['-POINTS-'].update(f'Points: {points}')
    window['-LEVEL-'].update(f'Level: {level}')
    window['-PROG-'].update_bar(progress, max_points)

# Event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '+1':
        update_progress(1)
    elif event == '+2':
        update_progress(2)
    elif event == 'Añadir':
        custom_add = values['-ADD_CUSTOM-']
        if custom_add and custom_add.isdigit():
            update_progress(int(custom_add))
    elif event == '-1':
        update_progress(-1)
    elif event == '-2':
        update_progress(-2)
    elif event == 'Remover':
        custom_remove = values['-REMOVE_CUSTOM-']
        if custom_remove and custom_remove.isdigit():
            update_progress(-int(custom_remove))

# Close the window
window.close()
