from string import letters
import string
import re
import random
import hmac
import hashlib

secret = 'AmandaBynes'

def is_printable(s):
	printset = set(string.printable)
	return set(s).issubset(printset)

def link_as_dict(name, link):
	return {'name': name, 'link': link}


####################################################################################################
# Password and Secure Cookie Functions
####################################################################################################
def make_secure_value(value):
	return value + '|' + hmac.new(secret, value).hexdigest()

def check_secure_value(secure_value):
	value = str(secure_value).split('|')[0]
	if secure_value == make_secure_value(value):
		return value

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_password_hash(password, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(password + salt).hexdigest()
	return h + '|' + salt

def validate_password(password, h):
	salt = h.split('|')[1]
	return h == make_password_hash(password, salt)


####################################################################################################
# Login Requirements and Validation Functions
####################################################################################################
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or EMAIL_RE.match(email)