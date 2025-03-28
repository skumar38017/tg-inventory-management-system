# frontend/app/app.py
from flask import Flask
from .entry_inventory import main as entry_inventory_main


app = Flask(__name__)

# Home Route
@app.route('/')
def home():
    try:
        entry_inventory_main()  # Example call to a function from entry_inventory.py
        return "Inventory System Running!"
    except Exception as e:
        return f"Error occurred: {str(e)}"

# Run the Flask Application
if __name__ == '__main__':
    app.run(debug=True)

