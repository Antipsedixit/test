#!/usr/bin/env python3
"""Simple cross-platform repost agent skeleton for X, Facebook, Instagram.

Uses official APIs (when configured) and sqlite deduplication.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Post:
    source: str
    post_id: str
    text: str
    created_at: str
    media_urls: tuple[str, ...] = ()


class StateStore:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reposted (
                source TEXT NOT NULL,
                post_id TEXT NOT NULL,
                published_at TEXT NOT NULL,
                PRIMARY KEY(source, post_id)
            )
            """
        )
        self.conn.commit()

    def seen(self, post: Post) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM reposted WHERE source = ? AND post_id = ?",
            (post.source, post.post_id),
        ).fetchone()
        return row is not None

    def mark(self, post: Post) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO reposted(source, post_id, published_at) VALUES(?,?,?)",
            (post.source, post.post_id, dt.datetime.now(tz=dt.timezone.utc).isoformat()),
        )
        self.conn.commit()


class SourceClient:
    def fetch_recent(self) -> List[Post]:
        raise NotImplementedError


class XSource(SourceClient):
    def __init__(self, bearer_token: str, username: str, max_results: int = 5):
        self.bearer_token = bearer_token
        self.username = username
        self.max_results = max_results

    def _request(self, url: str) -> dict:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {self.bearer_token}")
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode("utf-8"))

    def fetch_recent(self) -> List[Post]:
        user_url = (
            f"https://api.x.com/2/users/by/username/{urllib.parse.quote(self.username)}"
            "?user.fields=id"
        )
        user_json = self._request(user_url)
        user_id = user_json["data"]["id"]

        posts_url = (
            f"https://api.x.com/2/users/{user_id}/tweets"
            f"?max_results={self.max_results}&tweet.fields=created_at,text,id"
        )
        posts_json = self._request(posts_url)

        results: List[Post] = []
        for item in posts_json.get("data", []):
            results.append(
                Post(
                    source=f"x:{self.username}",
                    post_id=item["id"],
                    text=item.get("text", ""),
                    created_at=item.get("created_at", ""),
                )
            )
        return results


class JsonFileSource(SourceClient):
    """Local fallback source for dry-runs and testing."""

    def __init__(self, path: str, source_name: str):
        self.path = path
        self.source_name = source_name

    def fetch_recent(self) -> List[Post]:
        with open(self.path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        posts: List[Post] = []
        for item in payload:
            posts.append(
                Post(
                    source=self.source_name,
                    post_id=str(item["id"]),
                    text=item.get("text", ""),
                    created_at=item.get("created_at", ""),
                    media_urls=tuple(item.get("media_urls", [])),
                )
            )
        return posts


class Publisher:
    def publish(self, post: Post) -> None:
        raise NotImplementedError


class WebhookPublisher(Publisher):
    """Generic publisher to automation tools (Make/Zapier/custom webhook).

    You can route the webhook to platform-specific actions for Instagram/Facebook/X.
    """

    def __init__(self, webhook_url: str, channel_name: str):
        self.webhook_url = webhook_url
        self.channel_name = channel_name

    def publish(self, post: Post) -> None:
        body = {
            "channel": self.channel_name,
            "source": post.source,
            "post_id": post.post_id,
            "text": post.text,
            "created_at": post.created_at,
            "media_urls": list(post.media_urls),
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.webhook_url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=20):
            return


class StdoutPublisher(Publisher):
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    def publish(self, post: Post) -> None:
        print(
            f"[DRY-RUN] publish to {self.channel_name}: "
            f"{post.source}/{post.post_id} => {post.text[:90]}"
        )


def load_sources(config: dict, dry_run: bool) -> List[SourceClient]:
    sources: List[SourceClient] = []
    for item in config.get("sources", []):
        typ = item["type"]
        if typ == "x":
            if dry_run:
                continue
            token = os.getenv(item.get("bearer_env", "X_BEARER_TOKEN"))
            if not token:
                raise ValueError(
                    f"Missing bearer token env for X source '{item['name']}'. "
                    f"Set {item.get('bearer_env', 'X_BEARER_TOKEN')}"
                )
            sources.append(XSource(token, item["username"], item.get("max_results", 5)))
        elif typ == "json_file":
            sources.append(JsonFileSource(item["path"], item["name"]))
        else:
            raise ValueError(f"Unsupported source type: {typ}")
    return sources


def load_publishers(config: dict, dry_run: bool) -> List[Publisher]:
    pubs: List[Publisher] = []
    for item in config.get("destinations", []):
        name = item["name"]
        if dry_run:
            pubs.append(StdoutPublisher(name))
            continue
        webhook = item.get("webhook_url") or os.getenv(item.get("webhook_env", ""))
        if not webhook:
            raise ValueError(
                f"Missing webhook for destination '{name}'. "
                "Set webhook_url in config or webhook_env env var."
            )
        pubs.append(WebhookPublisher(webhook, name))
    return pubs


def run(config_path: str, state_path: str, dry_run: bool = False) -> int:
    with open(config_path, "r", encoding="utf-8") as fh:
        config = json.load(fh)

    sources = load_sources(config, dry_run=dry_run)
    publishers = load_publishers(config, dry_run=dry_run)
    state = StateStore(state_path)

    published = 0
    for source in sources:
        try:
            posts = source.fetch_recent()
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            print(f"[WARN] failed to fetch source: {exc}", file=sys.stderr)
            continue

        for post in reversed(posts):
            if state.seen(post):
                continue
            for pub in publishers:
                try:
                    pub.publish(post)
                except urllib.error.URLError as exc:
                    print(f"[WARN] publish failed: {exc}", file=sys.stderr)
                    continue
            state.mark(post)
            published += 1

    print(f"Done. New posts handled: {published}")
    return 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-platform repost agent")
    parser.add_argument("--config", default="agent/config.example.json")
    parser.add_argument("--state-db", default="agent/state.db")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return run(args.config, args.state_db, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
