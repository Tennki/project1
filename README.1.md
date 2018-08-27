git clone https://github.com/bosha/flask-app-structure-example/
cd flask-app-structure-example
virtualenv -p python3 env
source env/bin/activate
pip install -r requipments/development.txt
export APP_SETTINGS="config.DevelopmentConfig"
# DBUSERNAME, DBPASSWORD и DBNAME необходимо заменить на свои реквизиты доступа к БД
export DATABASE_URL='postgresql://DBUSERNAME:DBPASSWORD@localhost/DBNAME'
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver





