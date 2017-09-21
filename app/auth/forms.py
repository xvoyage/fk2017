from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from flask_login import current_user

class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Length(1,64),
												Email()])
	password = PasswordField('password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')


class RegistrationForm(Form):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	username = StringField('Username',validators=[
		Required(), Length(1,64), Regexp('^[A-Za-z][A-za-z0-9_.]*$', 0,
											'Username must have only letters,')])
	password = PasswordField('Password', validators=[
		Required(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confim password', validators=[Required()])
	submit = SubmitField('Register')


	def validate_email(self,field):
		if User.query.filter_by(emali=field.data).first():
			raise ValidationError('Email already registered')


	def vilidate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use')


class ChangePwdForm(Form):
	old_password = PasswordField('Old Password', validators=[Required()])
	new_password = PasswordField('New Password', validators=[
			Required(), EqualTo('new_password2', message="Password must Match.")])
	new_password2 = PasswordField('Confim Password', validators=[Required()])
	submit = SubmitField('Save')


	def validate_old_password(self, field):
		if not current_user.verify_password(field.data):
			raise ValidationError("Password Not Match.")


class Changeemail(Form):
	new_email = StringField('New Email', validators=[Required(), Email()])
	submit = SubmitField('Save')

	def validate_new_email(self,field):
		if User.query.filter_by(emali=field.data).first():
			raise ValidationError("Email already in use")
