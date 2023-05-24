from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, User
from schema import CreateUser, PatchUser, VALIDATION_CLASS
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


app = Flask('app')


class HttpError(Exception):

    def __init__(self, status_code: int, message: dict | list | str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    error_message = {
        'status': 'eror',
        'description': error.message
    }
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response


def validate_json(json_data: dict, validation_model: VALIDATION_CLASS):
    try:
        model_obj = validation_model(**json_data)
        model_obj_dict = model_obj.dict()
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    return model_obj_dict


def get_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, message='User не существует')
    return user


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            return jsonify({'id': user.id,
                            'username': user.username,
                            'description': user.description,
                            'title': user.title,
                            'creation_time': user.creation_time.isoformat()})

    def post(self):
        json_data = validate_json(request.json, CreateUser)
        with Session() as session:
            user = User(**json_data)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, f'{json_data["username"]} is busy')
            return jsonify({'id': user.id,
                            'username': user.username,
                            'description': user.description,
                            'title': user.title,
                            'creation_time': user.creation_time.isoformat()})

    def patch(self,user_id: int):
        json_data = validate_json(request.json, PatchUser)
        with Session() as session:
            user = get_user(session, user_id)
            for field, value in json_data.items():
                setattr(user, field, value)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, f'{json_data["username"]} is busy')
            return jsonify({'id': user.id,
                            'username': user.username,
                            'description': user.description,
                            'title': user.title,
                            'creation_time': user.creation_time.isoformat()})

    def dellete(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            session.delete(user)
            session.commit()
            return jsonify({'status': 'success'})


app.add_url_rule(
    '/user/<int:user_id>',
    view_func=UserView.as_view('with_user_id'),
    methods=['GET', 'PATCH', 'DELETE']
)

app.add_url_rule(
    '/user/',
    view_func=UserView.as_view('create_user'),
    methods=['POST']
)


if __name__ == '__main__':
    app.run()