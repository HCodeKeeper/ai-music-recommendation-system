export class Song {
  constructor(data) {
    this.id = data.id || data.song_id;
    this.name = data.name || data.title;
    this.artist = data.artist;
    this.album = data.album;
    this.genre = data.genre;
    this.duration = data.duration;
    this.pathToTrack = data.pathToTrack || data.path_to_track;
    this.recommendationExplanation = data.recommendation_explanation;
    this.features = data.features || {};
    this.isLiked = data.isLiked || false;
  }

  static fromApiResponse(data) {
    return new Song(data);
  }

  get displayTitle() {
    return `${this.name} - ${this.artist}`;
  }

  get isPlayable() {
    return Boolean(this.pathToTrack);
  }

  get formattedDuration() {
    if (!this.duration) return '';
    const minutes = Math.floor(this.duration / 60);
    const seconds = Math.floor(this.duration % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
}

export const createSong = (data) => new Song(data); 