echo @off
pip install -r requirements.txt
del __pycache__
del app/__pycache__
del instance
del base.db
cls
py app.py