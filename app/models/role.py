from app.extensions import db
from datetime import datetime
from app.models.permission import role_permissions


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles")

    def has_permission(self, permission_name):
        return any(p.name == permission_name or p.codename == permission_name for p in self.permissions)

    def __repr__(self):
        return f"<Role {self.name}>"
