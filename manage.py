import os
from app import create_app, db
from app.models import Admin,Case


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Admin=Admin ,Case=Case)



if __name__ == '__main__':
    app.run()
