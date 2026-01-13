#!/usr/bin/env python3
"""
RSS.com Podcast Episode Publisher
Automatically publishes generated podcast episodes to RSS.com via API v4

Requirements:
- pip install requests python-dotenv
- Environment variables: RSS_COM_API_KEY, RSS_COM_PODCAST_ID
- API documentation: https://api.rss.com/v4/docs

Usage:
    python scripts/publish_to_rss.py --date 2026-01-13
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv


class RSSComPublisher:
    """Publisher for RSS.com API v4"""

    API_BASE_URL = "https://api.rss.com/v4"

    def __init__(self, api_key: str, podcast_id: str):
        """
        Initialize RSS.com publisher

        Args:
            api_key: RSS.com API key from dashboard
            podcast_id: RSS.com podcast ID (network ID)
        """
        self.api_key = api_key
        self.podcast_id = podcast_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        })

    def publish_episode(
        self,
        audio_file: Path,
        cover_image: Path,
        title: str,
        description: str,
        pub_date: Optional[datetime] = None
    ) -> Dict:
        """
        Publish a podcast episode to RSS.com

        Args:
            audio_file: Path to MP3 file
            cover_image: Path to cover image (PNG/JPG)
            title: Episode title
            description: Episode description
            pub_date: Publication date (defaults to now)

        Returns:
            API response as dictionary

        Raises:
            requests.HTTPError: If API request fails
        """
        if pub_date is None:
            pub_date = datetime.now()

        # Upload audio file
        print(f"📤 Uploading audio file: {audio_file.name} ({audio_file.stat().st_size / 1024 / 1024:.1f}MB)")
        audio_url = self._upload_file(audio_file)

        # Upload cover image
        print(f"🖼️  Uploading cover image: {cover_image.name} ({cover_image.stat().st_size / 1024:.1f}KB)")
        image_url = self._upload_file(cover_image)

        # Create episode
        print(f"📝 Creating episode: {title}")
        episode_data = {
            "title": title,
            "description": description,
            "audioUrl": audio_url,
            "imageUrl": image_url,
            "pubDate": pub_date.isoformat(),
            "status": "published"  # or "draft" for review before publishing
        }

        response = self.session.post(
            f"{self.API_BASE_URL}/podcasts/{self.podcast_id}/episodes",
            json=episode_data
        )
        response.raise_for_status()

        result = response.json()
        print(f"✅ Episode published successfully!")
        print(f"   Episode ID: {result.get('id', 'N/A')}")
        print(f"   Episode URL: {result.get('url', 'N/A')}")

        return result

    def _upload_file(self, file_path: Path) -> str:
        """
        Upload a file to RSS.com storage

        Args:
            file_path: Path to file

        Returns:
            Public URL of uploaded file

        Raises:
            requests.HTTPError: If upload fails
        """
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f, self._get_mime_type(file_path))
            }

            # Note: Actual endpoint may be different - check API docs
            # This is a common pattern for file upload endpoints
            response = self.session.post(
                f"{self.API_BASE_URL}/upload",
                files=files
            )
            response.raise_for_status()

            result = response.json()
            return result.get("url") or result.get("fileUrl")

    @staticmethod
    def _get_mime_type(file_path: Path) -> str:
        """Get MIME type from file extension"""
        mime_types = {
            ".mp3": "audio/mpeg",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg"
        }
        return mime_types.get(file_path.suffix.lower(), "application/octet-stream")


def parse_script_metadata(script_file: Path) -> Dict[str, str]:
    """
    Extract metadata from generated markdown script

    Args:
        script_file: Path to script-YYYY-MM-DD.md

    Returns:
        Dictionary with title, date, article_count, categories
    """
    with open(script_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    metadata = {}

    # Parse header (first 10 lines typically contain metadata)
    for line in lines[:10]:
        line = line.strip()
        if line.startswith("# "):
            metadata["title"] = line[2:].strip()
        elif line.startswith("**日期**:"):
            metadata["date"] = line.split(":", 1)[1].strip()
        elif line.startswith("**文章数**:"):
            metadata["article_count"] = line.split(":", 1)[1].strip()
        elif line.startswith("**分类**:"):
            metadata["categories"] = line.split(":", 1)[1].strip()

    return metadata


def generate_episode_description(script_file: Path, metadata: Dict[str, str]) -> str:
    """
    Generate episode description from script content

    Args:
        script_file: Path to markdown script
        metadata: Parsed metadata

    Returns:
        Episode description text
    """
    with open(script_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract news headlines (lines starting with ### in 新闻内容 section)
    headlines = []
    in_news_section = False
    for line in content.split("\n"):
        if "## 新闻内容" in line:
            in_news_section = True
        elif line.startswith("## ") and in_news_section:
            break
        elif in_news_section and line.startswith("### "):
            headlines.append(line[4:].strip())

    description_parts = [
        f"今日科技早报 - {metadata.get('date', 'N/A')}",
        "",
        f"📊 本期内容: {metadata.get('article_count', 'N/A')}篇 {metadata.get('categories', '科技, 商业')} 领域新闻",
        "",
        "📰 今日头条:",
    ]

    for i, headline in enumerate(headlines[:5], 1):  # Top 5 headlines
        description_parts.append(f"{i}. {headline}")

    description_parts.extend([
        "",
        "🎙️ AI播报员为您精选每日科技动态,把握行业脉搏。",
        "",
        f"#科技播客 #AI播报 #{metadata.get('categories', '科技')}"
    ])

    return "\n".join(description_parts)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Publish podcast episode to RSS.com")
    parser.add_argument(
        "--date",
        required=True,
        help="Episode date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Base output directory (default: output)"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Verify required environment variables
    api_key = os.getenv("RSS_COM_API_KEY")
    podcast_id = os.getenv("RSS_COM_PODCAST_ID")

    if not api_key:
        print("❌ ERROR: RSS_COM_API_KEY environment variable not set")
        print("   Get your API key from: https://rss.com/dashboard → Account → API Keys")
        sys.exit(1)

    if not podcast_id:
        print("❌ ERROR: RSS_COM_PODCAST_ID environment variable not set")
        print("   Find your podcast ID in the RSS.com dashboard URL")
        sys.exit(1)

    # Locate episode files
    base_path = Path(args.output_dir) / args.date / "dailyReport"

    audio_file = base_path / f"podcast-{args.date}.mp3"
    cover_file = base_path / f"cover-{args.date}.png"
    script_file = base_path / f"script-{args.date}.md"

    # Verify all files exist
    missing_files = []
    for file_path in [audio_file, cover_file, script_file]:
        if not file_path.exists():
            missing_files.append(str(file_path))

    if missing_files:
        print(f"❌ ERROR: Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        sys.exit(1)

    print(f"📦 Found all required files for {args.date}")

    # Parse episode metadata
    metadata = parse_script_metadata(script_file)
    title = metadata.get("title", f"今日科技早报 - {args.date}")
    description = generate_episode_description(script_file, metadata)

    print(f"\n📋 Episode Details:")
    print(f"   Title: {title}")
    print(f"   Date: {args.date}")
    print(f"   Articles: {metadata.get('article_count', 'N/A')}")
    print(f"   Categories: {metadata.get('categories', 'N/A')}")
    print()

    # Publish to RSS.com
    try:
        publisher = RSSComPublisher(api_key, podcast_id)
        pub_date = datetime.strptime(args.date, "%Y-%m-%d")

        result = publisher.publish_episode(
            audio_file=audio_file,
            cover_image=cover_file,
            title=title,
            description=description,
            pub_date=pub_date
        )

        print(f"\n🎉 Publication completed successfully!")
        print(f"   RSS Feed: https://rss.com/podcasts/{podcast_id}/feed.xml")

    except requests.HTTPError as e:
        print(f"\n❌ API Error: {e.response.status_code} {e.response.reason}")
        try:
            error_detail = e.response.json()
            print(f"   Details: {error_detail}")
        except Exception:
            print(f"   Response: {e.response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
