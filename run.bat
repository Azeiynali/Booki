echo @off
pip install -r requirements.txt
del pycache
del app/pycache
del instance
py app.py