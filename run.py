from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from .env
app = create_app()

if __name__ == '__main__':
    # Set debug status based on ENV
    app.run(debug=os.getenv("FLASK_ENV", "development") == "development")
