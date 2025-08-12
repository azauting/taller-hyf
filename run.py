from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)  # <- NECESARIO para habilitar flask db

if __name__ == "__main__":
    app.debug = False
    app.run()