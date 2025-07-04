import streamlit_authenticator as stauth

hasher = stauth.Hasher()
hashed_password = hasher.hash('123')
print(hashed_password)