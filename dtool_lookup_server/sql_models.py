from dtool_lookup_server import sql_db as db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return '<User {}, is_admin={}>'.format(self.username, self.is_admin)

    def as_dict(self):
        """Return user using dictionary representation."""
        return {
            "username": self.username,
            "is_admin": self.is_admin,
            "base_uris": [],
        }
