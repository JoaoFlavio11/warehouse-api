import  firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

#inicializar o firebase auth
def initialize_firebase():
    if not firebase_admin._apps:
      cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")

initialize_firebase()

def verify_firebase_token(token):
  """
  Verifica token do Firebase e retorna dados do usuário
  """
  try:
    decoded_token = auth.verify_id_token(token)
    return {
      'uid': decoded_token['uid'],
      'email': decoded_token.get('email'),
      'email_verified': decoded_token.get('email_verified', False),
    }
  except Exception as e:
    return None
