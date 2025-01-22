from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods = ['GET', 'POST'])
def messages():
    response = make_response({"error": "No Messages"}, 404)
    if request.method == 'GET':
        all_messages = Message.query.order_by(Message.created_at).all()
        response = make_response([message.to_dict() for message in all_messages],200)
    elif request.method == 'POST':
        try:
            a = request.get_json()
            new_message = Message(
                body = a.get("body"),
                username = a.get("username"),
                created_at = a.get("created_at"),
                updated_at = a.get("updated_at")
                )
            db.session.add(new_message)
            db.session.commit()

            response = make_response(new_message.to_dict(), 201)
        except Exception as e:
            response = make_response({"error": f"{e}", "request object": f"{request}"}, 404)

    return response


@app.route('/messages/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id = id).first()
    response = make_response({"error": "No such message"}, 404)
    if message:
        if request.method == 'GET':
            response = make_response(message.to_dict(), 200)
        elif request.method =='PATCH':
            a = request.get_json()
            for attr in a:
                setattr(message, attr, a[attr])
            db.session.add(message)
            db.session.commit()

            response = make_response(message.to_dict(), 200)
        else:
            db.session.delete(message)
            db.session.commit()

            response = make_response({"Success": "Message deleted"}, 200)
    return response


if __name__ == '__main__':
    app.run(port=5555)
