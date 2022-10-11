Software Requirements:
    Python - https://www.python.org/downloads/
    Visual Studio Code - https://code.visualstudio.com/
    GitHub Desktop - https://desktop.github.com/
    MySQL Workbench - https://dev.mysql.com/downloads/workbench/

Extension Requirements:
    Better Jinja

Package Requirements:
Open a terminal with ctrl + `, and type "pip install package_name" to install the following:
    flask
    flask-login
    flask_sqlalchemy
    sqlalchemy
    pymysql
    cryptography
    azure-core
    azure-storage-blob
    
If there is an issue with the code not working in the init.py file, change line 44 & 45 to
with app.app_context():
    db.create_all()







 
