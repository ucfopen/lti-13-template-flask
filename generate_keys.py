import json

from Crypto.PublicKey import RSA
from jwcrypto.jwk import JWK

from main import db
from main import LTIConfig

# LTIConfig Reference
# class LTIConfig(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     iss = db.Column(db.Text)
#     client_id = db.Column(db.Text)
#     auth_login_url = db.Column(db.Text)
#     auth_token_url = db.Column(db.Text)
#     key_set_url = db.Column(db.Text)
#     private_key_file = db.Column(db.Text)
#     public_key_file = db.Column(db.Text)
#     deployment_id = db.Column(db.Text)

print("Creating Database if it doesn't exist...")
db.create_all()
print("Starting key generation...")

key = RSA.generate(4096)
print("Generating Private Key...")
private_key = key.exportKey()
print("Generating Public Key...")
public_key = key.publickey().exportKey()

print("Converting Keys to JWKS...")
jwk_obj = JWK.from_pem(public_key)
public_jwk = json.loads(jwk_obj.export_public())
public_jwk["alg"] = "RS256"
public_jwk["use"] = "sig"
public_jwk_str = json.dumps(public_jwk)

canvas_url = """
What is your canvas url?
1 - https://canvas.instructure.com/
2 - https://canvas.test.instructure.com/
3 - Other
"""
print(canvas_url)
server_url = input()
if server_url == "1":
    server_url = "https://canvas.instructure.com"
if server_url == "2":
    server_url = "https://canvas.test.instructure.com"
if server_url == "3":
    print("Please type your server url: ")
    server_url = input()

if ".test." in server_url:
    issuer = "https://canvas.test.instructure.com"
else:
    issuer = "https://canvas.instructure.com"


lticonfig = LTIConfig(
    iss=issuer,
    client_id="CHANGEME",
    auth_login_url="%s/api/lti/authorize_redirect" % server_url,
    auth_token_url="%s/login/oauth2/token" % server_url,
    key_set_url="%s/api/lti/security/jwks" % server_url,
    private_key_file=private_key.decode("utf-8"),
    public_key_file=public_key.decode("utf-8"),
    public_jwk=public_jwk_str,
    deployment_id="{CHANGEME:CHANGEME}",
)


db.session.add(lticonfig)
db.session.commit()

print("JSON url: http://127.0.0.1:8000/lti13template/config/%s/json" % lticonfig.id)

message = """
You will now need to install the tool into your LMS, and update the Deployment ID
and Client ID via your database manager of choice, or from here:
"""

print(message)

print("Client ID: ")
client_id = input()

print("Deployment ID: ")
deployment_id = input()

lticonfig.deployment_id = deployment_id
lticonfig.client_id = client_id

db.session.add(lticonfig)
db.session.commit()
