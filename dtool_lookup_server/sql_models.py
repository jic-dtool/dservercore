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


# How long can a base URI be?
# Amazon s3 bucket names are 3-63 characters.
# Microsoft Azure storage account names are 3 to 24 characters.
class BaseURI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_uri = db.Column(db.String(255), index=True, unique=True)

    def __repr__(self):
        return '<BaseURI {}>'.format(self.base_uri)

    def as_dict(self):
        """Return base URI using dictionary representation."""
        return {
            "base_uri": self.base_uri,
            "users_with_search_permissions": [],
            "users_with_register_permissions": [],
        }
