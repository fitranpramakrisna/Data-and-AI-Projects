from application import db

class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    statusName = db.Column(db.String(length=10), nullable=False)

    def __repr__(self):
        return f'Message {self.text}'
