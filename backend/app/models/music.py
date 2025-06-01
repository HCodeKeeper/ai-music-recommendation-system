from .. import db

class Music(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.String(4))
    bpm = db.Column(db.Float)
    energy = db.Column(db.Float)
    danceability = db.Column(db.Float)
    loudness = db.Column(db.Float)
    liveness = db.Column(db.Float)
    valence = db.Column(db.Float)
    duration = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    tags = db.Column(db.String(1000))
    key = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    speechiness = db.Column(db.Float)
    time_signature = db.Column(db.Integer)
    pathToTrack = db.Column(db.String(500))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'genre': self.genre,
            'year': self.year,
            'bpm': self.bpm,
            'energy': self.energy,
            'danceability': self.danceability,
            'loudness': self.loudness,
            'liveness': self.liveness,
            'valence': self.valence,
            'duration': self.duration,
            'acousticness': self.acousticness,
            'instrumentalness': self.instrumentalness,
            'tags': self.tags,
            'key': self.key,
            'mode': self.mode,
            'speechiness': self.speechiness,
            'time_signature': self.time_signature,
            'pathToTrack': self.pathToTrack
        } 