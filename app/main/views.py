from flask import render_template, session, redirect, url_for, flash,request, current_app, make_response
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Permission, Role, Post,Follow, Comment
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from flask import abort

@main.route('/', methods=['GET', 'POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and \
			form.validate_on_submit():
		post = Post(body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))

	show_followed_posts = False
	if current_user.is_authenticated:
		show_followed_posts = bool(request.cookies.get('show_followed', ''))
	if show_followed_posts:
		query = current_user.followed_posts
	else:
		query = Post.query

	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('index.html', form=form, posts=posts,
					pagination=pagination, show_followed=show_followed_posts)


@main.route('/all')
@login_required
def show_all():
	rep = make_response(redirect(url_for('.index')))
	rep.set_cookie('show_followed', '', max_age=30*24*60*60)
	return rep

@main.route('/follower')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
	return resp

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
	return "For administrator"


@main.route('/Moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
	return "For comment moderators!"

@main.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	posts = user.posts.order_by(Post.timestamp.desc()).all()
	return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your Profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.username
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user)
	if form.validate_on_submit():
		user.emali = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('THe profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.emali
	form.username.data =user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET','POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
							post=post,
							author=current_user._get_current_object())
		db.session.add(comment)
		flash('Your comment has been published.')
		return redirect(url_for('.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() -1 ) / \
			current_app.config['FLASKY_POSTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('post.html', posts=[post], form=form,
							comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and \
			not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated.')
		return redirect(url_for('.post', id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user'), username=username)
	current_user.follow(user)
	flash('You are now following %s .' % username)
	return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You not Following ')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash('You are now unfollow.')
	return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
@login_required
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect('.index')

	if user.id != current_user.id:
		flash("You Can't see the follower.")
		return redirect(url_for('.user', username=username))

	page = request.args.get('page', 1, type=int)
	pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
			page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
			error_out=False)

	followerslist = [{"user":f.follower.username, "timestamp":f.timestamp,
						"img":f.follower.gravatar(size=40),"status":user.is_following(f.follower)}
					for f in pagination.items]
	return render_template('/followers.html', user=user, follow=followerslist)


@main.route('/followed/<username>')
@login_required
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect('.index')

	if user.id != current_user.id:
		flash("You Can't see the follower.")
		return redirect(url_for('.user', username=username))

	followerslist = [{"user":f.followed.username, "timestamp":f.timestamp,
						"img":f.followed.gravatar(size=40)}
					for f in user.followed]
	return render_template('/followed.html', user=user, follow=followerslist)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('moderate.html', comments=comments,
							pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('.moderate',
			page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disabled/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	return redirect(url_for('.moderate',
		page=request.args.get('page', 1, type=int)))
