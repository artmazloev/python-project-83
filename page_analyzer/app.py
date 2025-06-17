from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(
    import_name=__name__,
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.get('/home')
def home():
    return "Hello world!"