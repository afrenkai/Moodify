import aiohttp
import asyncio
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)
load_dotenv()


class AsyncGeniusService:
    
    def __init__(self):
        self.access_token = os.getenv('GENIUS_ACCESS_TOKEN')
        self.base_url = "https://api.genius.com"
        self.cache = {}  
        
        if not self.access_token:
            logger.warning("Genius access token not found")
            
    def is_available(self) -> bool:
        return self.access_token is not None
    
    def _get_cache_key(self, song_name: str, artist: str) -> str:
        return hashlib.md5(f"{song_name}|{artist}".encode()).hexdigest()
    
    async def search_song_async(
        self, 
        session: aiohttp.ClientSession,
        song_name: str, 
        artist: str
    ) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None

        cache_key = self._get_cache_key(song_name, artist)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            query = f"{song_name} {artist}"
            url = f"{self.base_url}/search"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"q": query}
            
            async with session.get(
                url, 
                headers=headers, 
                params=params,
                timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                hits = data.get('response', {}).get('hits', [])
                
                if not hits:
                    return None
                

                result = hits[0].get('result', {})
                song_data = {
                    'title': result.get('title'),
                    'artist': result.get('primary_artist', {}).get('name'),
                    'url': result.get('url'),
                    'song_id': result.get('id')
                }
                
                self.cache[cache_key] = song_data
                return song_data
                
        except Exception as e:
            logger.debug(f"Error searching Genius: {e}")
            return None
    
    def extract_emotional_keywords(self, lyrics: str) -> Dict[str, int]:
        if not lyrics:
            return {}
        
        emotion_keywords = {
            'happy': ['happy', 'joy', 'smile', 'laugh', 'celebrate', 'bright', 'sunshine', 
                      'good', 'wonderful', 'amazing', 'fantastic', 'cheerful', 'delight',
                      'fun', 'party', 'dancing', 'excited', 'glad', 'blessed', 'thrill',
                      'euphoria', 'ecstatic', 'bliss', 'grin', 'giggle', 'cheer', 'jolly',
                      'merry', 'gleeful', 'elated', 'jubilant', 'radiant', 'golden'],
            
            'sad': ['sad', 'cry', 'tear', 'lonely', 'heartbreak', 'miss', 'lost', 'pain',
                    'hurt', 'broken', 'empty', 'alone', 'sorrow', 'grief', 'blue', 'down',
                    'depressed', 'misery', 'suffering', 'ache', 'weep', 'mourn', 'sobbing',
                    'despair', 'hopeless', 'darkness', 'gloom', 'somber', 'melancholy',
                    'heavy', 'numb', 'hollow', 'forsaken', 'abandoned', 'dejected'],
            
            'love': ['love', 'heart', 'together', 'forever', 'kiss', 'embrace', 'darling',
                     'baby', 'dear', 'sweet', 'romance', 'passion', 'desire', 'need',
                     'want', 'adore', 'cherish', 'devotion', 'affection', 'tender',
                     'intimate', 'lover', 'beloved', 'soulmate', 'valentine', 'crush',
                     'infatuation', 'enamored', 'yearning', 'longing', 'attracted'],
            
            'angry': ['angry', 'rage', 'hate', 'fight', 'scream', 'mad', 'burn',
                      'fury', 'violent', 'destroy', 'break', 'smash', 'kill', 'blood',
                      'war', 'enemy', 'revenge', 'fire', 'furious', 'wrath', 'outrage',
                      'fierce', 'savage', 'brutal', 'hostile', 'aggression', 'venom',
                      'spite', 'bitter', 'resentment', 'grudge', 'storm', 'thunder'],
            
            'hopeful': ['hope', 'dream', 'believe', 'faith', 'future', 'tomorrow', 'rise',
                        'better', 'new', 'change', 'light', 'shine', 'star', 'wish',
                        'possible', 'trust', 'prayer', 'dawn', 'sunrise', 'begin',
                        'start', 'fresh', 'optimistic', 'inspire', 'aspire', 'vision',
                        'miracle', 'fortune', 'blessed', 'lucky', 'chance', 'opportunity'],
            
            'nostalgic': ['remember', 'memory', 'past', 'yesterday', 'used to', 'back when',
                          'once', 'before', 'old', 'time', 'moment', 'ago', 'reminisce',
                          'recall', 'forgotten', 'history', 'childhood', 'younger', 'summer',
                          'seasons', 'photographs', 'letters', 'vintage', 'ancient',
                          'faded', 'dusty', 'previous', 'former', 'expired', 'bygone'],
            
            'energetic': ['run', 'dance', 'move', 'jump', 'wild', 'alive', 'fire',
                          'fast', 'quick', 'rush', 'power', 'energy', 'strong', 'loud',
                          'intense', 'explosive', 'electric', 'pumped', 'adrenaline',
                          'charged', 'dynamic', 'vigorous', 'fierce', 'blazing', 'roar',
                          'thunder', 'lightning', 'ignite', 'spark', 'burst', 'surge'],
            
            'calm': ['calm', 'peace', 'quiet', 'still', 'gentle', 'soft', 'breathe',
                     'slow', 'rest', 'relax', 'tranquil', 'serene', 'silent', 'sleep',
                     'whisper', 'soothe', 'ease', 'drift', 'float', 'mellow', 'laid',
                     'chill', 'steady', 'smooth', 'mild', 'placid', 'composed'],
            
            'melancholic': ['melancholy', 'wistful', 'bittersweet', 'longing', 'yearning',
                            'regret', 'lament', 'mourn', 'fade', 'dusk', 'autumn', 'rain',
                            'gray', 'cold', 'distant', 'echoes', 'shadows', 'ghosts',
                            'twilight', 'fading', 'waning', 'decline', 'diminish', 'slip',
                            'drift', 'dissolve', 'vanish', 'haunt', 'linger', 'trace'],
            
            'romantic': ['romantic', 'lover', 'intimate', 'tender', 'gentle', 'close',
                         'touch', 'hold', 'warm', 'soft', 'beautiful', 'eyes', 'gaze',
                         'caress', 'cuddle', 'snuggle', 'whisper', 'moonlight', 'candlelight',
                         'roses', 'flowers', 'serenade', 'enchanted', 'charmed', 'swept'],
            
            'anxious': ['anxious', 'worry', 'fear', 'scared', 'nervous', 'panic', 'stress',
                        'tension', 'pressure', 'uncertain', 'doubt', 'restless', 'uneasy',
                        'afraid', 'terrified', 'dread', 'paranoid', 'frantic', 'troubled',
                        'distressed', 'overwhelmed', 'crisis', 'chaos', 'confusion',
                        'shaking', 'trembling', 'racing', 'breathless', 'trapped'],
            
            'peaceful': ['peaceful', 'harmony', 'balance', 'zen', 'meditation', 'nature',
                         'ocean', 'breeze', 'sunset', 'morning', 'stillness', 'sanctuary',
                         'haven', 'oasis', 'garden', 'meadow', 'valley', 'river', 'stream',
                         'mountain', 'sky', 'clouds', 'birds', 'gentle', 'flowing'],
            
            # Additional nuanced emotions
            'tired': ['tired', 'exhausted', 'weary', 'drained', 'fatigue', 'worn',
                      'sleepy', 'drowsy', 'spent', 'depleted', 'sluggish', 'languid',
                      'lethargic', 'weak', 'faint', 'heavy', 'burden', 'weight'],
            
            'confident': ['confident', 'proud', 'strong', 'bold', 'brave', 'fearless',
                          'unstoppable', 'invincible', 'powerful', 'mighty', 'champion',
                          'winner', 'conqueror', 'triumph', 'victory', 'glory', 'crown',
                          'throne', 'king', 'queen', 'boss', 'legend', 'hero'],
            
            'rebellious': ['rebel', 'break', 'rules', 'free', 'wild', 'chaos', 'riot',
                           'revolution', 'fight', 'resist', 'defy', 'against', 'outlaw',
                           'renegade', 'maverick', 'anarchist', 'underground', 'punk'],
            
            'playful': ['play', 'fun', 'silly', 'joke', 'laugh', 'tease', 'flirt',
                        'game', 'trick', 'prank', 'mischief', 'cheeky', 'witty',
                        'clever', 'humorous', 'amusing', 'entertaining', 'lighthearted'],
            
            'sensual': ['body', 'skin', 'lips', 'touch', 'taste', 'feel', 'sensation',
                        'desire', 'heat', 'sweat', 'breathe', 'pulse', 'rhythm',
                        'slow', 'deep', 'intense', 'curves', 'smooth', 'silk'],
            
            'empowered': ['power', 'strong', 'rise', 'fight', 'stand', 'voice', 'speak',
                          'roar', 'warrior', 'survivor', 'overcome', 'conquer', 'unbreakable',
                          'resilient', 'fierce', 'determined', 'unstoppable', 'force'],
            
            'vulnerable': ['vulnerable', 'fragile', 'delicate', 'exposed', 'raw', 'open',
                           'honest', 'naked', 'bare', 'confession', 'admit', 'reveal',
                           'truth', 'weakness', 'human', 'imperfect', 'flawed'],
            
            'mysterious': ['mystery', 'secret', 'shadow', 'dark', 'hidden', 'unknown',
                           'enigma', 'puzzle', 'cryptic', 'strange', 'whisper', 'midnight',
                           'moon', 'veil', 'mask', 'lurk', 'fog', 'mist', 'obscure'],
            
            'dreamy': ['dream', 'fantasy', 'imagine', 'surreal', 'ethereal', 'floating',
                       'cloud', 'sky', 'stars', 'cosmic', 'universe', 'magical',
                       'enchanted', 'mystical', 'otherworldly', 'transcendent', 'drift'],
            
            'grateful': ['grateful', 'thankful', 'appreciate', 'bless', 'fortune', 'lucky',
                         'gift', 'treasure', 'precious', 'value', 'honor', 'privilege',
                         'grace', 'mercy', 'kindness', 'generosity', 'abundance'],
            
            'lonely': ['lonely', 'alone', 'solitude', 'isolated', 'separate', 'distant',
                       'apart', 'missing', 'absence', 'void', 'empty', 'silence',
                       'nobody', 'solo', 'single', 'deserted', 'stranded', 'abandoned'],
            
            'inspired': ['inspire', 'motivation', 'driven', 'passion', 'create', 'build',
                         'achieve', 'realize', 'manifest', 'purpose', 'calling', 'destiny',
                         'potential', 'greatness', 'excellence', 'brilliance', 'genius'],
            
            'conflicted': ['torn', 'divided', 'confused', 'stuck', 'between', 'choice',
                           'dilemma', 'struggle', 'battle', 'conflict', 'war', 'fight',
                           'against', 'within', 'question', 'doubt', 'maybe', 'perhaps'],
            
            'carefree': ['carefree', 'easy', 'breezy', 'light', 'simple', 'wandering',
                         'roaming', 'drifting', 'floating', 'lazy', 'casual', 'relaxed',
                         'spontaneous', 'adventure', 'explore', 'discover', 'journey'],
        }
        
        lyrics_lower = lyrics.lower()
        scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(lyrics_lower.count(word) for word in keywords)
            if count > 0:
                scores[emotion] = count
        
        return scores
    
    def compute_emotion_match_score(
        self, 
        emotional_keywords: Dict[str, int],
        target_emotion: str
    ) -> float:
        """
        Compute how well the lyrics match the target emotion.
        Uses direct matching and semantic relationships between emotions.
        
        Args:
            emotional_keywords: Dict of emotion -> keyword count from lyrics
            target_emotion: The emotion we're trying to match
            
        Returns:
            Score from 0.0 to 1.0
        """
        if not emotional_keywords:
            return 0.0
        
        target_emotion = target_emotion.lower().strip()
        
        # Direct match - highest score
        if target_emotion in emotional_keywords:
            direct_score = emotional_keywords[target_emotion]
            total_keywords = sum(emotional_keywords.values())
            
            normalized = direct_score / max(total_keywords, 1)
            return min(1.0, normalized * 2.0)  # Boost direct matches

        # Expanded semantic relationships between emotions
        related_emotions = {
            'happy': {
                'love': 0.7, 'hopeful': 0.7, 'energetic': 0.6, 'playful': 0.8,
                'grateful': 0.7, 'confident': 0.6, 'carefree': 0.8, 'inspired': 0.6
            },
            'sad': {
                'melancholic': 0.9, 'nostalgic': 0.7, 'anxious': 0.6, 'lonely': 0.9,
                'vulnerable': 0.7, 'conflicted': 0.6, 'tired': 0.5
            },
            'energetic': {
                'happy': 0.6, 'angry': 0.7, 'confident': 0.8, 'rebellious': 0.7,
                'empowered': 0.8, 'playful': 0.6, 'inspired': 0.7
            },
            'calm': {
                'peaceful': 0.9, 'hopeful': 0.5, 'dreamy': 0.7, 'carefree': 0.6,
                'grateful': 0.5, 'tired': 0.5
            },
            'angry': {
                'energetic': 0.7, 'anxious': 0.6, 'rebellious': 0.8, 'empowered': 0.6,
                'conflicted': 0.6
            },
            'melancholic': {
                'sad': 0.9, 'nostalgic': 0.8, 'lonely': 0.8, 'vulnerable': 0.7,
                'mysterious': 0.5, 'dreamy': 0.5
            },
            'hopeful': {
                'happy': 0.7, 'peaceful': 0.5, 'inspired': 0.8, 'empowered': 0.7,
                'confident': 0.6, 'grateful': 0.7
            },
            'romantic': {
                'love': 0.9, 'happy': 0.6, 'peaceful': 0.5, 'dreamy': 0.6,
                'sensual': 0.8, 'playful': 0.5, 'vulnerable': 0.6
            },
            'anxious': {
                'sad': 0.6, 'angry': 0.6, 'conflicted': 0.8, 'vulnerable': 0.7,
                'tired': 0.6, 'lonely': 0.5
            },
            'peaceful': {
                'calm': 0.9, 'hopeful': 0.5, 'dreamy': 0.7, 'grateful': 0.6,
                'carefree': 0.6
            },
            'tired': {
                'calm': 0.5, 'sad': 0.5, 'melancholic': 0.6, 'peaceful': 0.4,
                'vulnerable': 0.5, 'lonely': 0.5
            },
            'confident': {
                'energetic': 0.8, 'empowered': 0.9, 'happy': 0.6, 'rebellious': 0.6,
                'inspired': 0.7
            },
            'rebellious': {
                'angry': 0.8, 'energetic': 0.7, 'confident': 0.6, 'empowered': 0.7
            },
            'playful': {
                'happy': 0.8, 'energetic': 0.6, 'carefree': 0.7, 'love': 0.5
            },
            'sensual': {
                'romantic': 0.8, 'love': 0.7, 'mysterious': 0.5, 'dreamy': 0.4
            },
            'empowered': {
                'confident': 0.9, 'energetic': 0.8, 'rebellious': 0.7, 'inspired': 0.8,
                'hopeful': 0.7, 'angry': 0.5
            },
            'vulnerable': {
                'sad': 0.7, 'anxious': 0.7, 'romantic': 0.6, 'melancholic': 0.7,
                'lonely': 0.6, 'honest': 0.8
            },
            'mysterious': {
                'dreamy': 0.7, 'melancholic': 0.5, 'sensual': 0.5, 'anxious': 0.4
            },
            'dreamy': {
                'calm': 0.7, 'peaceful': 0.7, 'mysterious': 0.7, 'romantic': 0.6,
                'hopeful': 0.5, 'nostalgic': 0.5
            },
            'grateful': {
                'happy': 0.7, 'hopeful': 0.7, 'peaceful': 0.6, 'love': 0.6,
                'calm': 0.5
            },
            'lonely': {
                'sad': 0.9, 'melancholic': 0.8, 'nostalgic': 0.6, 'vulnerable': 0.6,
                'anxious': 0.5
            },
            'inspired': {
                'hopeful': 0.8, 'energetic': 0.7, 'empowered': 0.8, 'confident': 0.7,
                'happy': 0.6
            },
            'conflicted': {
                'anxious': 0.8, 'sad': 0.6, 'angry': 0.6, 'vulnerable': 0.7,
                'melancholic': 0.6
            },
            'carefree': {
                'happy': 0.8, 'calm': 0.6, 'peaceful': 0.6, 'playful': 0.7,
                'dreamy': 0.5
            },
            'love': {
                'romantic': 0.9, 'happy': 0.7, 'grateful': 0.6, 'vulnerable': 0.5,
                'sensual': 0.7
            },
            'nostalgic': {
                'melancholic': 0.8, 'sad': 0.7, 'peaceful': 0.4, 'dreamy': 0.5,
                'lonely': 0.6
            }
        }

        # Calculate weighted score from related emotions
        if target_emotion in related_emotions:
            related_score = 0.0
            max_possible_score = 0.0
            
            for related_emotion, weight in related_emotions[target_emotion].items():
                if related_emotion in emotional_keywords:
                    related_score += emotional_keywords[related_emotion] * weight
                max_possible_score += weight * 5  # Assume max 5 mentions per emotion
            
            if max_possible_score > 0:
                normalized_score = related_score / max_possible_score
                return min(0.8, normalized_score * 1.5)  # Cap related matches at 0.8
        
        # Fallback: check if any detected emotions are in our target's related list
        for detected_emotion, count in emotional_keywords.items():
            if detected_emotion in related_emotions:
                if target_emotion in related_emotions[detected_emotion]:
                    weight = related_emotions[detected_emotion][target_emotion]
                    total_keywords = sum(emotional_keywords.values())
                    normalized = (count / max(total_keywords, 1)) * weight
                    return min(0.7, normalized * 1.5)  # Cap reverse matches at 0.7
        
        return 0.0
    
    async def get_song_with_emotional_profile(
        self,
        session: aiohttp.ClientSession,
        song_name: str,
        artist: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get song metadata with emotional profile from Genius.
        
        NOTE: Uses lyricsgenius library in background for actual lyrics extraction.
        This method only returns emotional analysis, not lyrics content.
        
        Args:
            session: aiohttp client session
            song_name: Name of the song
            artist: Artist name
            
        Returns:
            Dict with emotional profile or None
        """
        if not self.is_available():
            return None
        
        cache_key = self._get_cache_key(song_name, artist)
        if cache_key in self.cache:
            cached = self.cache.get(cache_key)
            if cached and 'emotional_profile' in cached:
                return cached
        
        try:
            song_data = await self.search_song_async(session, song_name, artist)
            if not song_data:
                return None
            
            return song_data
            
        except Exception as e:
            logger.debug(f"Error getting emotional profile: {e}")
            return None
    
    async def get_lyrics_async(
        self,
        session: aiohttp.ClientSession,
        song_url: str
    ) -> Optional[str]:
        """
        Get lyrics for a song from Genius web scraping.
        
        Note: This requires web scraping which may be unreliable.
        For production, consider using lyricsgenius library.
        
        Args:
            session: aiohttp client session
            song_url: Genius song URL
            
        Returns:
            Lyrics text or None
        """
        return None
    
    async def batch_get_emotional_profiles(
        self,
        songs: List[Tuple[str, str]],
        target_emotion: Optional[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get emotional profiles for multiple songs concurrently.
        Uses lyricsgenius in thread pool to avoid blocking.
        
        Args:
            songs: List of (song_name, artist) tuples
            target_emotion: Optional target emotion for scoring
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping "song_name|artist" to emotional profile with scores
        """
        if not self.is_available():
            return {}
        
        try:
            import lyricsgenius
        except ImportError:
            logger.warning("lyricsgenius not installed, skipping lyrics analysis")
            return {}
        
        results = {}
        
        genius = lyricsgenius.Genius(
            self.access_token,
            timeout=5,
            retries=1,
            sleep_time=0.2,
            verbose=False,
            remove_section_headers=True
        )
        
        async def get_profile_for_song(song_name: str, artist: str):
            """Get emotional profile for a single song."""
            try:
                loop = asyncio.get_event_loop()
                song = await loop.run_in_executor(
                    None, 
                    lambda: genius.search_song(song_name, artist)
                )
                
                if not song or not song.lyrics:
                    return None
                
                emotional_keywords = self.extract_emotional_keywords(song.lyrics)
                
                emotion_score = 0.0
                if target_emotion and emotional_keywords:
                    emotion_score = self.compute_emotion_match_score(
                        emotional_keywords,
                        target_emotion
                    )
                
                dominant_emotion = None
                if emotional_keywords:
                    dominant_emotion = max(emotional_keywords.items(), key=lambda x: x[1])[0]
                
                return {
                    'song_id': song.id,
                    'genius_url': song.url,
                    'emotional_keywords': emotional_keywords,
                    'dominant_emotion': dominant_emotion,
                    'emotion_match_score': emotion_score,
                    'word_count': len(song.lyrics.split()),
                    'has_lyrics': True
                }
                
            except Exception as e:
                logger.debug(f"Could not get profile for {song_name}: {e}")
                return None
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def get_with_semaphore(song_name: str, artist: str):
            async with semaphore:
                return await get_profile_for_song(song_name, artist)
        
        tasks = [get_with_semaphore(song_name, artist) for song_name, artist in songs]
        
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0  # 15 second total timeout
            )
            
            for (song_name, artist), response in zip(songs, responses):
                if isinstance(response, dict) and response:
                    key = f"{song_name}|{artist}"
                    results[key] = response
                    cache_key = self._get_cache_key(song_name, artist)
                    self.cache[cache_key] = response
                    
        except asyncio.TimeoutError:
            logger.warning("Batch emotional profile extraction timed out")
        
        logger.info(f"Got emotional profiles for {len(results)}/{len(songs)} songs")
        return results
    
    def batch_get_emotional_profiles_sync(
        self,
        songs: List[Tuple[str, str]],
        target_emotion: Optional[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Synchronous wrapper for batch_get_emotional_profiles.
        
        Args:
            songs: List of (song_name, artist) tuples
            target_emotion: Optional target emotion for scoring
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping "song_name|artist" to emotional profile
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.batch_get_emotional_profiles(songs, target_emotion, max_concurrent)
        )
    
    async def batch_search_songs(
        self,
        songs: List[Tuple[str, str]],
        max_concurrent: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        Search for multiple songs concurrently.
        
        Args:
            songs: List of (song_name, artist) tuples
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping "song_name|artist" to song data
        """
        if not self.is_available():
            return {}
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def search_with_semaphore(song_name: str, artist: str):
                async with semaphore:
                    return await self.search_song_async(session, song_name, artist)
            
            tasks = [
                search_with_semaphore(song_name, artist)
                for song_name, artist in songs
            ]
            
            try:
                responses = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=10.0  # 10 second total timeout
                )
                
                for (song_name, artist), response in zip(songs, responses):
                    if isinstance(response, dict):
                        key = f"{song_name}|{artist}"
                        results[key] = response
                        
            except asyncio.TimeoutError:
                logger.warning("Batch search timed out")
        
        return results
    
    def batch_search_songs_sync(
        self,
        songs: List[Tuple[str, str]],
        max_concurrent: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        Synchronous wrapper for batch_search_songs.
        
        Args:
            songs: List of (song_name, artist) tuples
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping "song_name|artist" to song data
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.batch_search_songs(songs, max_concurrent)
        )
