import dtoolcore.utils

from dtool_lookup_server import sql_db as db

search_permissions = db.Table(
    "search_permissions",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True
    ),
    db.Column(
        "base_uri_id",
        db.Integer,
        db.ForeignKey("base_uri.id"),
        primary_key=True
    )
)

register_permissions = db.Table(
    "register_permissions",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True
    ),
    db.Column(
        "base_uri_id",
        db.Integer,
        db.ForeignKey("base_uri.id"),
        primary_key=True
    )
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    search_base_uris = db.relationship(
        "BaseURI",
        secondary=search_permissions,
        back_populates="search_users"
    )
    register_base_uris = db.relationship(
        "BaseURI",
        secondary=register_permissions,
        back_populates="register_users"
    )

    def __repr__(self):
        return '<User {}, is_admin={}>'.format(self.username, self.is_admin)

    def as_dict(self):
        """Return user using dictionary representation."""
        return {
            "username": self.username,
            "is_admin": self.is_admin,
            "search_permissions_on_base_uris":
                [u.base_uri for u in self.search_base_uris],
            "register_permissions_on_base_uris":
                [u.base_uri for u in self.register_base_uris],
        }


# How long can a base URI be?
# Amazon s3 bucket names are 3-63 characters.
# Microsoft Azure storage account names are 3 to 24 characters.
class BaseURI(db.Model):
    __tablename__ = "base_uri"
    id = db.Column(db.Integer, primary_key=True)
    base_uri = db.Column(db.String(255), index=True, unique=True)
    search_users = db.relationship(
        "User",
        secondary=search_permissions,
        back_populates="search_base_uris"
    )
    register_users = db.relationship(
        "User",
        secondary=register_permissions,
        back_populates="register_base_uris"
    )
    datasets = db.relationship("Dataset", back_populates="base_uri")

    def __repr__(self):
        return '<BaseURI {}>'.format(self.base_uri)

    def as_dict(self):
        """Return base URI using dictionary representation."""
        return {
            "base_uri": self.base_uri,
            "users_with_search_permissions":
                [u.username for u in self.search_users],
            "users_with_register_permissions":
                [u.username for u in self.register_users],
        }


# How long can a URI be?
# How long can a dataset name be?
#   => dtool-create enforces names that are max 80 chars
class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_uri_id = db.Column(
        db.Integer,
        db.ForeignKey('base_uri.id'),
        nullable=False
    )
    uri = db.Column(db.String(255), index=True, unique=True, nullable=False)
    uuid = db.Column(db.String(36), index=True, nullable=False)
    name = db.Column(db.String(80), index=True, nullable=False)
    base_uri = db.relationship("BaseURI", back_populates="datasets")
    creator_username = db.Column(db.String(255), index=True, nullable=False)
    frozen_at = db.Column(db.DateTime(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return '<Dataset {}>'.format(self.uri)

    def as_dict(self):
        """Return user using dictionary representation."""
        return {
            "base_uri": self.base_uri.base_uri,
            "uri": self.uri,
            "uuid": self.uuid,
            "name": self.name,
            "creator_username": self.creator_username,
            "frozen_at": dtoolcore.utils.timestamp(self.frozen_at),
            "created_at": dtoolcore.utils.timestamp(self.created_at),
        }
