import boto3
import os
import hashlib
import urllib.parse
import json

from datetime import datetime
from flask import Flask, request, render_template, session, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from pylti1p3.contrib.flask import (FlaskOIDCLogin, FlaskMessageLaunch, FlaskRequest,
                                    FlaskCacheDataStorage)
from pylti1p3.deep_link_resource import DeepLinkResource
from pylti1p3.exception import LtiException
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.registration import Registration

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask('lti-13-example', template_folder='templates')
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']
app.wsgi_app = ReverseProxied(app.wsgi_app)
cache = Cache(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ============================================
# Extended Classes in pylti1p3 lib
# ============================================

class ExtendedFlaskMessageLaunch(FlaskMessageLaunch):

    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just skip nonce validation.

        """
        iss = self.get_iss()
        deep_link_launch = self.is_deep_link_launch()

        if iss == "http://imsglobal.org" and deep_link_launch:
            return self
        return super(ExtendedFlaskMessageLaunch, self).validate_nonce()

    def validate_deployment(self):
            iss = self._get_iss()
            deployment_id = self._get_deployment_id()
            tool_conf = get_lti_config(session['iss'], session['client_id'])

            # Find deployment.
            deployment = self._tool_config.find_deployment(iss, deployment_id)
            if deployment_id in tool_conf._config[iss][0]['deployment_ids'][0]:
                deployment = True
            if not deployment:
                raise LtiException("Unable to find deployment")

            return self



# ============================================
# DB Models
# ============================================

class LTIConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iss = db.Column(db.Text)
    client_id = db.Column(db.Text)
    auth_login_url = db.Column(db.Text)
    auth_token_url = db.Column(db.Text)
    key_set_url = db.Column(db.Text)
    private_key_file = db.Column(db.Text)
    public_key_file = db.Column(db.Text)
    public_jwk = db.Column(db.Text)
    deployment_id = db.Column(db.Text)



def get_lti_config(iss, client_id):
    lti = LTIConfig.query.filter_by(iss=iss, client_id=client_id).first()

    settings = {
            lti.iss: [{
                "client_id": lti.client_id,
                "auth_login_url": lti.auth_login_url,
                "auth_token_url": lti.auth_token_url,
                "auth_audience": "null",
                "key_set_url": lti.key_set_url,
                "key_set": None,
                "deployment_ids": [lti.deployment_id]
            }]
        }

    private_key = lti.private_key_file
    public_key = lti.public_key_file
    tool_conf = ToolConfDict(settings)

    tool_conf.set_private_key(iss, private_key, client_id=client_id)
    tool_conf.set_public_key(iss, public_key, client_id=client_id)

    return tool_conf


# ============================================
# Utilities
# ============================================


@app.context_processor
def utility_processor():
    def google_analytics():
        return app.config["GOOGLE_ANALYTICS"]

    return dict(google_analytics=google_analytics())


def get_launch_data_storage():
    return FlaskCacheDataStorage(cache)


# ============================================
# LTI 1.3 Routes
# ============================================

# OIDC Login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    session['iss'] = request.values.get('iss')
    session['client_id'] = request.values.get('client_id')

    tool_conf = get_lti_config(session['iss'], session['client_id'])

    launch_data_storage = get_launch_data_storage()

    flask_request = FlaskRequest()

    target_link_uri = flask_request.get_param('target_link_uri')
    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')

    oidc_login = FlaskOIDCLogin(flask_request, tool_conf,
                                launch_data_storage=launch_data_storage)
    return oidc_login\
        .enable_check_cookies()\
        .redirect(target_link_uri)

# Main Launch URL
@app.route('/launch/', methods=['POST'])
def launch():
    tool_conf = get_lti_config(session['iss'], session['client_id'])

    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch(flask_request, tool_conf,
                                                launch_data_storage=launch_data_storage)

    message_launch_data = message_launch.get_launch_data()

    email = message_launch_data.get('email')

    session['canvas_email'] = email
    session['launch_id'] = message_launch.get_launch_id()
    session['error'] = False

    return render_template('start.htm.j2', { 'email': email })

# Install JSON
@app.route('/config/<key_id>/json', methods=['GET'])
def config_json(key_id):
    title = "Simple LTI 1.3"
    description = "Simple LTI 1.3 Example"

    public_jwk = LTIConfig.query.filter_by(id=key_id).first()
    public_jwk = json.loads(public_jwk.public_jwk)

    target_link_uri = url_for('launch', _external=True)
    oidc_initiation_url = url_for('login', _external=True)

    config = {
        "title": title,
        "scopes": [],
        "extensions": [
            {
                "platform": "canvas.instructure.com",
                "settings": {
                    "platform": "canvas.instructure.com",
                    "placements": [
                        {
                            "placement": "course_navigation",
                            "visibility": "admins",
                            "default": "disabled",
                            "message_type": "LtiResourceLinkRequest",
                            "target_link_uri": target_link_uri,
                        }
                    ]
                },
                "privacy_level": "public",
            }
        ],
        "public_jwk": public_jwk,
        "description": description,
        "custom_fields": {
            "canvas_user_id": "$Canvas.user.id",
            "canvas_course_id": "$Canvas.course.id",
        },
        "target_link_uri": target_link_uri,
        "oidc_initiation_url": oidc_initiation_url,
    }

    return jsonify(config)
