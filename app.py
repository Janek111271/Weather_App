from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
import requests
from wtforms.validators import DataRequired, Length
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ
from twilio.rest import Client
import schedule
import time

# Flask and database setup
app = Flask(__name__)
app.secret_key = "12312311"
Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    phone_n = Column(String)
    city_name = Column(String)


# Twilio and OpenWeatherMap credentials
account_sid = environ.get('SID')
auth_token = environ.get('TOKEN')
twilio_phone_number = environ.get('NUMBER')
map_API = environ.get('API')

# DB connect
db_user = environ.get('CLOUD_SQL_USERNAME')
db_password = environ.get('CLOUD_SQL_PASSWORD')
db_name = environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = environ.get('CLOUD_SQL_CONNECTION')

DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host=/cloudsql/{db_connection_name}'


# Forms setup
class PhoneForm(FlaskForm):
    phone_number = StringField(label='Phone number', validators=[DataRequired(), Length(min=12, message='Too Short')])
    city_name = StringField(label='City name', validators=[DataRequired()])


class DeletePhone(FlaskForm):
    phone_to_delete = StringField(label='Phone number', validators=[DataRequired()])


# Create the database engine and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def get_books_as_list():
    books_list = []
    books = session.query(Book).all()
    for book in books:
        book_dict = {
            'phone_number': book.phone_n,
            'city_name': book.city_name
        }
        books_list.append(book_dict)
    return books_list


def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={map_API}'
    response = requests.get(url)
    data = response.json()
    return data


def send_sms(phone_number, message):
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone_number
        )
        print(f"SMS sent to {phone_number} successfully.")
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}. Error: {str(e)}")


def send_weather_sms():
    phone_data = get_books_as_list()
    for entry in phone_data:
        phone_number = entry['phone_number']
        city_name = entry['city_name']
        weather_data = get_weather(city_name)
        weather_description = weather_data['weather'][0]['description']
        message = f"Weather in {city_name}: {weather_description}"
        send_sms(phone_number, message)


# Send SMS when the Flask app starts
send_weather_sms()


@app.route('/')
def start():
    return redirect(url_for('form'))


@app.route('/form', methods=['GET', 'POST'])
def form():
    phone_upload = PhoneForm()
    phone_delete = DeletePhone()
    if phone_upload.validate_on_submit():
        phone = phone_upload.phone_number.data
        city_name = phone_upload.city_name.data
        new_number = Book(phone_n=phone, city_name=city_name)
        session.add(new_number)
        session.commit()
        return redirect(url_for('form'))
    if phone_delete.validate_on_submit():
        phone_to_delete = phone_delete.phone_to_delete.data
        deleted_phone = session.query(Book).filter_by(phone_n=phone_to_delete).first()
        if deleted_phone:
            session.delete(deleted_phone)
            session.commit()

    return render_template('form.html', form=phone_upload, delete=phone_delete)


if __name__ == '__main__':
    # Start the scheduled job
    schedule.every(1).hour.do(send_weather_sms)

    # Start the Flask app
    app.run()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)
