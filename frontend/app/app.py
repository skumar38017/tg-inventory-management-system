# frontend/app/app.py
from flask import Flask
import subprocess
import sys

app = Flask(__name__)

@app.route('/')
def home():
    try:
        subprocess.Popen([sys.executable, "-m", "app.entry_inventory"])
        return "Tkinter GUI launched in background!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=5555)


# from flask import Flask
# import subprocess
# import os

# app = Flask(__name__)

# @app.route('/')
# def home():
#     try:
#         # Set DISPLAY environment variable
#         env = os.environ.copy()
#         env['DISPLAY'] = os.getenv('DISPLAY', ':0')
        
#         # Launch Tkinter app
#         subprocess.Popen(
#             ['python', '/app/entry_inventory.py'],
#             env=env
#         )
#         return "Tkinter GUI launched in background!"
#     except Exception as e:
#         return f"Error: {str(e)}"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5555)