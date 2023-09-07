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

# Define your database URL
DATABASE_URL = 'sqlite:///phone_book.db'


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    phone_n = Column(String)
    city_c = Column(String)


class PhoneForm(FlaskForm):
    phone_number = StringField(label='Phone number', validators=[DataRequired(), Length(min=12, message='Too Short')])
    city_code = StringField(label='City number', validators=[DataRequired()])


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
            'id': book.id,
            'phone_number': book.phone_n,
            'city_code': book.city_c
        }
        books_list.append(book_dict)
    return books_list


@app.route('/')
def start():
    return redirect(url_for('form'))


@app.route('/form', methods=['GET', 'POST'])
def form():
    phone_upload = PhoneForm()
    number = get_books_as_list()
    if phone_upload.validate_on_submit():
        phone = phone_upload.phone_number.data  # Access the form field using .data
        city = phone_upload.city_code.data  # Access the form field using .data
        new_number = Book(phone_n=phone, city_c=city)
        session.add(new_number)
        session.commit()
        return redirect(url_for('form'))
    return render_template('form.html', form=phone_upload, list=number)


if __name__ == '__main__':
    app.run()
