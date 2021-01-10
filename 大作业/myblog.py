from realm_app import app
from flask_sqlalchemy import SQLAlchemy

# mysql://127.0.0.1:3306/day14?serverTimezone=CTT

if __name__ == '__main__':
    app.run(debug=True)

