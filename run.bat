echo @off
pip install -r requirements.txt
del __pycache__
del app/__pycache__
del instance
cls
py app.py