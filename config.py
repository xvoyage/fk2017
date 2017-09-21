import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True



	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URI') or 'mysql://root:samyshan@localhost/python'
	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'shanhaihang@163.com'
	MAIL_PASSWORD = 'QQlangshan2416'
	MAIL_SENDER = 'shanhaihang@163.com'
	FLASKY_ADMIN = '304035020@qq.com'
	FLASKY_POSTS_PER_PAGE = 10


config = {'development':DevelopmentConfig,'default':DevelopmentConfig}
