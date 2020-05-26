import os
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


class SignUpForm(FlaskForm):
    username= StringField('username',validators=[DataRequired(), Length(min=2,max=20)])
    email= StringField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        user_data=username.data
        user=db.execute("SELECT username FROM users WHERE username LIKE :user_data",{"user_data":user_data},).fetchone()
        print(user)
        if user:
            raise ValidationError('Username Taken')
    
    def validate_email(self,email):
        email_data=email.data
        user=db.execute("SELECT email FROM users WHERE email LIKE :email_data",{"email_data":email_data},).fetchone()
        print(email_data)
        if user:
            raise ValidationError('Someone already registered with this email')

class LoginForm(FlaskForm):
    username= StringField('username',validators=[DataRequired(), Length(min=2,max=20)])
    password=PasswordField('password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')