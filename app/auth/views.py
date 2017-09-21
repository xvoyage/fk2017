from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePwdForm, Changeemail
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(emali=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.user', username=current_user.username))
		flash('Invalid username or password.')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You has been logged out.')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	rgform = RegistrationForm()
	if rgform.validate_on_submit():
		user = User(emali=rgform.email.data,
					username=rgform.username.data,
					password=rgform.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.emali, 'Confirmation Your Account',
					'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you by email')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=rgform)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired')
	return redirect(url_for('main.index'))


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
	if current_user.set_newemail(token):
		flash('You confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired')
	return redirect(url_for('main.user', username=current_user.username))



@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
				and request.endpoint[:5] != 'auth.' \
				and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirmation():
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	token = current_user.generate_confirmation_token()
	send_email(current_user.emali, 'Confirm Account',
				'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.index'))

@auth.route('/changed-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePwdForm()
	if form.validate_on_submit():
		current_user.password = form.new_password.data
		db.session.add(current_user)
	return render_template('auth/changepassword.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = Changeemail()
	if form.validate_on_submit():
#		current_user.emali = form.new_email.data
#		current_user.confirmed = False
		token = current_user.generate_email_token(form.new_email.data)
		send_email(form.new_email.data, 'Confirmation Your Account', 'auth/email/change_email',
						user=current_user, token=token)
		flash('A confirmation email has been sent to you by email')
		return redirect(url_for('main.index'))
	return render_template('auth/Changeemail.html', form=form)
