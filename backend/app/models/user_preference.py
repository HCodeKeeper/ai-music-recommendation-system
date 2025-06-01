from .. import db
from datetime import datetime

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.String(50), db.ForeignKey('music.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('preferences', lazy='dynamic'))
    song = db.relationship('Music', backref=db.backref('user_preferences', lazy='dynamic'))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'song_id', name='unique_user_song'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_id': self.song_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'song': self.song.to_dict() if self.song else None
        } 