const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface SpotifyTrack {
	id: string;
	name: string;
	artist: string;
	album?: string;
	preview_url?: string;
	similarity_score: number;
	external_url?: string;
	duration_ms?: number;
	popularity?: number;
	album_image?: string;
}

export interface SpotifyArtist {
	id: string;
	name: string;
	genres: string[];
	popularity: number;
	image_url?: string;
	external_url: string;
}

export interface PlaylistGenerationRequest {
	songs?: Array<{
		song_name: string;
		artist: string;
		spotify_id?: string;
	}>;
	artists?: Array<{
		artist_name: string;
		spotify_id?: string;
	}>;
	emotion?: string[];
	num_results?: number;
	enrich_with_lyrics?: boolean;
}

export interface PlaylistGenerationResponse {
	playlist: SpotifyTrack[];
	emotion_features?: Record<string, number>;
	combined_embedding?: number[];
}

export interface SpotifyAPIError {
	error: string;
	details?: string;
}

export class SpotifyAPI {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	async generatePlaylist(
		request: PlaylistGenerationRequest
	): Promise<PlaylistGenerationResponse> {
		try {
			const response = await fetch(`${this.baseUrl}/generate-playlist`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(request),
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Failed to generate playlist');
			}

			const data = await response.json();

			return {
				playlist: data.playlist.map((song: any) => ({
					id: song.spotify_id || `track-${Math.random().toString(36).substr(2, 9)}`,
					name: song.song_name,
					artist: song.artist,
					album: song.album,
					preview_url: song.preview_url,
					similarity_score: song.similarity_score,
					external_url: song.external_url,
					duration_ms: song.duration_ms,
					popularity: song.popularity,
					album_image: song.album_image,
				})),
				emotion_features: data.emotion_features,
				combined_embedding: data.combined_embedding,
			};
		} catch (error) {
			console.error('Spotify API Error:', error);
			throw error;
		}
	}


	async getEmotions(): Promise<string[]> {
		try {
			const response = await fetch(`${this.baseUrl}/emotions`);
			if (!response.ok) {
				throw new Error('Failed to fetch emotions');
			}
			const data = await response.json();
			return data.emotions;
		} catch (error) {
			console.error('Failed to get emotions:', error);
			return [
				'happy',
				'sad',
				'energetic',
				'calm',
				'angry',
				'melancholic',
				'hopeful',
				'romantic',
				'anxious',
				'peaceful',
			];
		}
	}


	async healthCheck(): Promise<{ status: string; version: string }> {
		try {
			const response = await fetch(`${this.baseUrl}/health`);
			if (!response.ok) {
				throw new Error('Health check failed');
			}
			return await response.json();
		} catch (error) {
			console.error('Health check error:', error);
			throw error;
		}
	}


	async searchByEmotion(
		emotion: string,
		numResults: number = 20
	): Promise<PlaylistGenerationResponse> {
		return this.generatePlaylist({
			emotion: [emotion],
			num_results: numResults,
		});
	}

	async getRecommendations(
		seedTracks: Array<{ name: string; artist: string; spotify_id?: string }>,
		emotion?: string,
		numResults: number = 20
	): Promise<PlaylistGenerationResponse> {
		return this.generatePlaylist({
			songs: seedTracks.map((track) => ({
				song_name: track.name,
				artist: track.artist,
				spotify_id: track.spotify_id,
			})),
			emotion: emotion ? [emotion] : undefined,
			num_results: numResults,
		});
	}


	async searchTrack(
		songName: string,
		artist?: string
	): Promise<any> {
		try {
			const params = new URLSearchParams({ song_name: songName, limit: '1' });
			if (artist) {
				params.append('artist', artist);
			}

			const response = await fetch(
				`${this.baseUrl}/spotify/search?${params.toString()}`
			);

			if (!response.ok) {
				throw new Error('Failed to search track');
			}

			const data = await response.json();
			return data.tracks && data.tracks.length > 0 ? data.tracks[0] : null;
		} catch (error) {
			console.error('Search track error:', error);
			throw error;
		}
	}

	async searchTracks(
		songName: string,
		artist?: string,
		limit: number = 10
	): Promise<SpotifyTrack[]> {
		try {
			const params = new URLSearchParams({
				song_name: songName,
				limit: limit.toString()
			});
			if (artist) {
				params.append('artist', artist);
			}

			const response = await fetch(
				`${this.baseUrl}/spotify/search?${params.toString()}`
			);

			if (!response.ok) {
				throw new Error('Failed to search tracks');
			}

			const data = await response.json();
			return (data.tracks || []).map((track: any) => ({
				id: track.spotify_id || track.id,
				name: track.song_name || track.name,
				artist: track.artist,
				album: track.album,
				preview_url: track.preview_url,
				similarity_score: 0,
				external_url: track.external_url,
				duration_ms: track.duration_ms,
				popularity: track.popularity,
				album_image: track.album_image,
			}));
		} catch (error) {
			console.error('Search tracks error:', error);
			return [];
		}
	}

	async searchArtists(
		artistName: string,
		limit: number = 10
	): Promise<SpotifyArtist[]> {
		try {
			const params = new URLSearchParams({
				artist_name: artistName,
				limit: limit.toString()
			});

			const response = await fetch(
				`${this.baseUrl}/spotify/artist/search?${params.toString()}`
			);

			if (!response.ok) {
				throw new Error('Failed to search artists');
			}

			const data = await response.json();
			return (data.artists || []).map((artist: any) => ({
				id: artist.spotify_id || artist.id,
				name: artist.name,
				genres: artist.genres || [],
				popularity: artist.popularity || 0,
				image_url: artist.image_url,
				external_url: artist.external_url,
			}));
		} catch (error) {
			console.error('Search artists error:', error);
			return [];
		}
	}

	async getTrackById(trackId: string): Promise<any> {
		try {
			const response = await fetch(`${this.baseUrl}/spotify/track/${trackId}`);

			if (!response.ok) {
				throw new Error('Failed to get track');
			}

			return await response.json();
		} catch (error) {
			console.error('Get track error:', error);
			throw error;
		}
	}
}

export const spotifyAPI = new SpotifyAPI();

