# ==============================================================================
# youtube.py - YouTube Download & Search Handler
# ==============================================================================
# This file handles all YouTube-related operations:
# - Searching for videos/audio
# - Downloading YouTube content using yt-dlp
# - Managing YouTube cookies for age-restricted content
# - Caching search results for better performance
# - Validating YouTube URLs
# ==============================================================================

import os
import re
import glob
import time
import yt_dlp
import random
import asyncio
import aiohttp
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
# [ပြင်ဆင်ပြီး] yt-search-python Package ၏ Standard Async ရေးထုံးအတိုင်း ပြောင်းလဲခြင်း
from youtubesearchpython.__future__ import Playlist, VideosSearch
from HasiiMusic import config, logger
from HasiiMusic.helpers import Track, utils

# ==============================================================================
# ⚠️ [ပြင်ဆင်ပြီး] YOUTUBE COOKIE စာသားများကို Netscape Tab format ပြောင်းလဲပြီးပါပြီ ⚠️
# ==============================================================================
YOUTUBE_COOKIES_DATA = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com  TRUE  /  TRUE  1771645301  LOGIN_INFO  AFmmF2swRQIhAPeUceY3QHqzUmr40ibIbZgxAb9C0zwq1ImKRaMISpNIAiBs69dacffXx_kY3qswguHzxtrEI0KSJhWQqJTAX6elXA:QUQ3MjNmd2ZpZFhPZy1SckY4VFRsZWVJNVlIMzFSNjgxdFRnN0xGODlrd0lwQzE3dDlpMHNVR29mdkoxalAzZW9NMXB2aER6Y1B5dUJXUFBIYTVrMUJpaHZvWXB3R3FYam81cnJzZ01sTm9jMVBjRXlBalVMSVlxWTIzZjFMQlJTbFk1YUl6cmhxejdUQ3JDUkZyb2t2cnhChF9FY1hHZWFR
.youtube.com  TRUE  /  TRUE  1803706157  PREF  f4=4000000&tz=America.Guatemala&f7=100&f5=20000
.youtube.com  TRUE  /  FALSE  1803702813  HSID  AzEwUruLom4-XwkQu
.youtube.com  TRUE  /  TRUE  1803702813  SSID  AaNOtVEgH6u3hTf4d
.youtube.com  TRUE  /  FALSE  1803702813  APISID  _jD5F8_c3ottRvgT/Aa5VGOj4XKWf2LCCK
.youtube.com  TRUE  /  TRUE  1803702813  SAPISID  gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com  TRUE  /  TRUE  1803702813  __Secure-1PAPISID  gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com  TRUE  /  TRUE  1803702813  __Secure-3PAPISID  gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com  TRUE  /  FALSE  1803702813  SID  g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6du3kTTZMAaC35pDqDg6S9wACgYKAc0SARcSFQHGX2Mib_wNmHUwm7igI6kgNUUKjxoVAUF8yKpSvCTlJ5W0ebCERn91LItz0076
.youtube.com  TRUE  /  TRUE  1803702813  __Secure-1PSID  g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6E_F_ZQsTPIwibfYawZU21QACgYKAdoSARcSFQHGX2MiX1ntOUefsMm8p5-weSszIBoVAUF8yKo5GBbitSFh-Ifhnrw33n3u0076
.youtube.com  TRUE  /  TRUE  1803702813  __Secure-3PSID  g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6Skiv6cFhVJxy1TZLLK2Q6AACgYKAbYSARcSFQHGX2MiC26Zfvg_y2-pyArWKMdOLRoVAUF8yKpn4Ekm94ZWwDvlxez8iuHT0076
.youtube.com  TRUE  /  TRUE  1800682167  __Secure-1PSIDTS  sidts-CjQB7I_69KExocpfh8AoXfbzwmrbIK5wyTo_4sQ8BahjOEDVpt1hfKUhHekuL1wpL5XZJlUYEAA
.youtube.com  TRUE  /  TRUE  1800682167  __Secure-3PSIDTS  sidts-CjQB7I_69KExocpfh8AoXfbzwmrbIK5wyTo_4sQ8BahjOEDVpt1hfKUhHekuL1wpL5XZJlUYEAA
.youtube.com  TRUE  /  FALSE  1800682170  SIDCC  AKEyXzUeAdH-92qHBG2XQoQlNfQ4IG9aVN0nGYw6p28tKEQSIZxSV2U5TH2F_lRC7Z-LvRkfpA
.youtube.com  TRUE  /  TRUE  1800682170  __Secure-1PSIDCC  AKEyXzU-apGpVVdOJDBAhcc11LGFm-vA_792uw1_WkxczQKCg40mSUY88r7Qcesii472nolYym4
.youtube.com  TRUE  /  TRUE  1800682170  __Secure-3PSIDCC  AKEyXzXGD5AVknQ6gY3Ycjt_U4rLGgjcOInYlMVCcI-8tvKHhzHMoLn-1hbDpX02yDelavQZhQ
.youtube.com  TRUE  /  TRUE  1784698151  VISITOR_INFO1_LIVE  VkCJsATDS9M
.youtube.com  TRUE  /  TRUE  1784698151  VISITOR_PRIVACY_METADATA  CgJNTRIEGgAgHw%3D%3D
.youtube.com  TRUE  /  TRUE  1784694813  __Secure-ROLLOUT_TOKEN  CJ3jx7ncs_iGrwEQ6_bNiev7igMY0-_Rx-qgkgM%3D
.youtube.com  TRUE  /  TRUE  0  YSC  NJSFiW2pzmY
"""

class YouTube:
    def __init__(self):
        """Initialize YouTube handler with configuration and caching."""
        self.base = "https://www.youtube.com/watch?v="  # Base YouTube URL
        self.cookies = []  # List of available cookie files
        self.checked = False  # Whether cookies directory has been checked
        self.warned = False  # Whether missing cookies warning has been shown

        # Create temporary cookie file from hardcoded string data
        self.cookie_file_path = self._create_temporary_cookie_file()

        # Regular expression to match YouTube URLs (videos, shorts, live, playlists)
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

        # Cache search results to reduce API calls (10 minute TTL)
        self.search_cache = {}  # {"query_video": (result, timestamp)}
        self.cache_time = {}  # Deprecated, using tuple in search_cache instead

        # **PERFORMANCE FIX**: Limit concurrent downloads to prevent bandwidth saturation
        self._download_semaphore = asyncio.Semaphore(5)  # Max 5 simultaneous downloads
        self._max_video_height = getattr(config, "VIDEO_MAX_HEIGHT", 1080)

    def _create_temporary_cookie_file(self) -> Optional[str]:
        """Convert the hardcoded cookie string into a clean, tab-separated Netscape file for yt-dlp."""
        if not YOUTUBE_COOKIES_DATA.strip() or "xxxxxxxxxx" in YOUTUBE_COOKIES_DATA:
            logger.warning("⚠️ Hardcoded YouTube cookies are empty or contain placeholder values.")
            return None
        
        try:
            temp_dir = tempfile.gettempdir()
            cookie_path = os.path.join(temp_dir, "hasii_direct_cookies.txt")
            
            cleaned_lines = []
            for line in YOUTUBE_COOKIES_DATA.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    cleaned_lines.append(line)
                    continue
                
                # spaces တွေကို ခွဲထုတ်ပြီး Standard Tab (\t) နဲ့ ပြန်စပ်ပေးခြင်း
                parts = re.split(r'\s+', line)
                if len(parts) >= 7:
                    cleaned_lines.append("\t".join(parts[:7]))
            
            with open(cookie_path, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(cleaned_lines) + "\n")
            
            logger.info(f"✅ Hardcoded cookies successfully formatted and loaded: {cookie_path}")
            return cookie_path
        except Exception as e:
            logger.error(f"❌ Failed to create temporary cookie file from code: {e}")
            return None

    def _locate_download_file(self, video_id: str, video: bool = False) -> Optional[str]:
        """Locate any completed download file for a video id."""
        pattern = f"downloads/{video_id}*"
        candidates = sorted([
            path for path in glob.glob(pattern)
            if not path.endswith((".part", ".ytdl", ".info.json", ".temp"))
        ])

        video_exts = {".mp4", ".mkv", ".webm", ".mov"}
        audio_exts = {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}

        if video:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in video_exts:
                    return path
        else:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in audio_exts:
                    return path

        for path in candidates:
            if os.path.isdir(path):
                continue
            return path
        return None

    def get_cookies(self):
        """Returns the temporary cookie file path if configured, otherwise falls back to folder search."""
        if self.cookie_file_path and os.path.exists(self.cookie_file_path):
            return self.cookie_file_path

        # Fallback to local cookies directory if code cookies are not set
        if not self.checked:
            if os.path.exists("HasiiMusic/cookies"):
                for file in os.listdir("HasiiMusic/cookies"):
                    if file.endswith(".txt"):
                        self.cookies.append(file)
            self.checked = True

        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return f"HasiiMusic/cookies/{random.choice(self.cookies)}"

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("🍪 Saving cookies from urls...")
        saved_count = 0
        for url in urls:
            try:
                path = f"HasiiMusic/cookies/cookie{random.randint(10000, 99999)}.txt"
                link = url.replace("me/", "me/raw/")
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as resp:
                        if resp.status != 200:
                            logger.error(f"❌ Cookie download failed: HTTP {resp.status} from {url}")
                            continue
                        content = await resp.read()
                        if not content or len(content) < 50:
                            logger.error(f"❌ Cookie file empty or invalid from {url}")
                            continue
                        
                        os.makedirs("HasiiMusic/cookies", exist_ok=True)
                        with open(path, "wb") as fw:
                            fw.write(content)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            saved_count += 1
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"✅ Saved: {cookie_filename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Cookie download error from {url}: {e}")
        
        self.checked = True
        if saved_count > 0:
            logger.info(f"✅ Cookies saved. ({saved_count} file(s))")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        messages = [message_1]
        link = None
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.URL:
                        link = text[entity.offset: entity.offset +
                                    entity.length]
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == enums.MessageEntityType.TEXT_LINK:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0].split("?si")[0]
        return None

    async def search(self, query: str, m_id: int) -> Track | None:
        cache_key = query
        current_time = asyncio.get_running_loop().time()

        if cache_key in self.search_cache:
            cached_result, cache_timestamp = self.search_cache[cache_key]
            if current_time - cache_timestamp < 600:  # 10 minutes
                fresh = replace(cached_result)
                fresh.message_id = m_id
                fresh.file_path = None
                fresh.user = None
                fresh.time = 0
                fresh.video = False
                return fresh

        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
        except Exception as e:
            logger.warning(f"⚠️ YouTube search failed for '{query}': {e}")
            return None

        if results and results["result"]:
            data = results["result"][0]
            duration = data.get("duration")
            is_live = duration is None or duration == "LIVE"

            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=duration if not is_live else "LIVE",
                duration_sec=0 if is_live else utils.to_seconds(duration),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get(
                    "thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                is_live=is_live,
            )

            self.search_cache[cache_key] = (track, current_time)
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(),
                                 key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]

            return replace(track)
        return None

    async def playlist(self, limit: int, user: str, url: str) -> list[Track]:
        try:
            plist = await Playlist.get(url)
            tracks = []

            if not plist or "videos" not in plist or not plist["videos"]:
                return []

            for data in plist["videos"][:limit]:
                try:
                    thumbnails = data.get("thumbnails", [])
                    thumbnail_url = ""
                    if thumbnails and len(thumbnails) > 0:
                        thumbnail_url = thumbnails[-1].get(
                            "url", "").split("?")[0]

                    link = data.get("link", "")
                    if "&list=" in link:
                        link = link.split("&list=")[0]

                    track = Track(
                        id=data.get("id", ""),
                        channel_name=data.get("channel", {}).get("name", ""),
                        duration=data.get("duration", "0:00"),
                        duration_sec=utils.to_seconds(
                            data.get("duration", "0:00")),
                        title=(data.get("title", "Unknown")[:25]),
                        thumbnail=thumbnail_url,
                        url=link,
                        user=user,
                        view_count="",
                    )
                    tracks.append(track)
                except Exception as e:
                    continue

            return tracks
        except KeyError as e:
            raise Exception(
                f"Failed to parse playlist. YouTube may have changed their structure.")
        except Exception as e:
            raise

    async def download(self, video_id: str, is_live: bool = False, video: bool = False) -> Optional[str]:
        url = self.base + video_id

        if is_live:
            cookie = self.get_cookies()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie,
                "format": "bestaudio/best",
                "noplaylist": True,
                "socket_timeout": 20,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # Live stream အတွက် ios client နှင့် po_token ပေါင်းစပ်ခြင်း
                "extractor_args": {
                    "youtube": {
                        "player_client": ["ios", "android"],
                        "po_token": ["web+web_embedded_player+QU9JQ2FzYmhSV0I0UWJ0b3Y0V0dCdTVwWVRmSUg2OW9uT29jSjFjSVRzdzdSRmxhVkt0UjN6Zkpxdmtidm1wZlJZSFlPcG1xTWRidmctOGxSTXZiZ213X2tlNGMxb1VqSkE9PQ=="]
                    }
                },
            }

            def _extract_url():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        if not info:
                            return None

                        direct = info.get("url")
                        if direct:
                            return direct

                        for fmt in info.get("formats", []):
                            if fmt.get("acodec") != "none" and fmt.get("url"):
                                return fmt["url"]

                        return info.get("manifest_url")
                    except Exception as ex:
                        logger.error("Live stream URL extraction failed: %s", ex)
                        return None

            try:
                stream_url = await asyncio.wait_for(asyncio.to_thread(_extract_url), timeout=35)
            except asyncio.TimeoutError:
                logger.error("Live stream URL extraction timed out for %s", video_id)
                return None

            return stream_url

        filename_pattern = f"downloads/{video_id}"
        
        existing_files = [
            f for f in glob.glob(f"{filename_pattern}.*")
            if not f.endswith('.part')
        ]
        if video:
            video_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}
            ]
            if video_candidates:
                return video_candidates[0]
        else:
            audio_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}
            ]
            if audio_candidates:
                return audio_candidates[0]

            container_fallbacks = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".mov"}
            ]
            if container_fallbacks:
                return container_fallbacks[0]
        
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            try:
                downloads_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"❌ Cannot create downloads directory: {e}")
                return None

        async with self._download_semaphore:
            cookie = self.get_cookies()
            base_opts = {
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "noplaylist": True,
                "geo_bypass": True,
                "no_warnings": True,
                "overwrites": False,
                "nocheckcertificate": True,
                "continuedl": True,
                "noprogress": True,
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 524288,
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # သာမန်ဒေါင်းလုဒ်အတွက် ios client နှင့် po_token ပေါင်းစပ်ခြင်း
                "extractor_args": {
                    "youtube": {
                        "player_client": ["ios", "android"],
                        "po_token": ["web+web_embedded_player+QU9JQ2FzYmhSV0I0UWJ0b3Y0V0dCdTVwWVRmSUg2OW9uT29jSjFjSVRzdzdSRmxhVkt0UjN6Zkpxdmtidm1wZlJZSFlPcG1xTWRidmctOGxSTXZiZ213X2tlNGMxb1VqSkE9PQ=="]
                    }
                },
            }

            if video:
                height_filter = ""
                if self._max_video_height and self._max_video_height > 0:
                    height_filter = f"[height<={self._max_video_height}]"
                format_chain = (
                    f"bestvideo[ext=mp4]{height_filter}+bestaudio[ext=m4a]/"
                    f"bestvideo{height_filter}+bestaudio/"
                    "bestvideo+bestaudio/best"
                )
                ydl_opts = {
                    **base_opts,
                    "format": format_chain,
                    "merge_output_format": "mp4",
                    "postprocessors": [
                        {
                            "key": "FFmpegVideoConvertor",
                            "preferedformat": "mp4",
                        }
                    ],
                }
            else:
                ydl_opts = {
                    **base_opts,
                    "format": "bestaudio[ext=m4a]/bestaudio[acodec=opus]/bestaudio/best",
                    "postprocessors": [],
                }

            ydl_opts_cookie = {
                **ydl_opts,
                "cookiefile": cookie,
            }

            def _download(ydl_runtime_opts):
                ydl_instance = None
                try:
                    ydl_instance = yt_dlp.YoutubeDL(ydl_runtime_opts)
                    info = ydl_instance.extract_info(url, download=True)
                    if not info:
                        return None
                    
                    time.sleep(0.5)
                    located = self._locate_download_file(video_id, video=video)
                    if located:
                        return located
                    return None
                except Exception as ex:
                    logger.warning(f"⚠️ Download process update: {ex}")
                    return self._locate_download_file(video_id, video=video)
                finally:
                    if ydl_instance:
                        try:
                            ydl_instance.close()
                        except Exception:
                            pass

            return await asyncio.to_thread(_download, ydl_opts_cookie)
