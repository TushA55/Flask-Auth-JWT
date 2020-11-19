import os
from app import app
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=(Path('.')  / '.env'))

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
if __name__ == "__main__":
    # app.run(debug=True, port=3000)
    app.run(debug=False)