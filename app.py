from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.secret_key = "12312311"
Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    phone_n = Column(String)
    city_c = Column(String)


class PhoneForm(FlaskForm):
    phone_number = StringField(label='Phone number', validators=[DataRequired(), Length(min=12, message='Too Short')])
    city_code = StringField(label='City number', validators=[DataRequired()])


engine = create_engine('sqlite:///phone_book.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    phone_upload = PhoneForm()
    if phone_upload.validate_on_submit():
        phone = phone_upload['phone_number']
        city = phone_upload['city_code']
        new_number = Book(phone_n=phone, city_c=city)
        session.add(new_number)
        session.commit()
    return render_template('index.html', form=phone_upload)


if __name__ == '__main__':
    app.run()
