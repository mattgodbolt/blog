#!/usr/bin/env python

import http.server
import os
import shutil
import subprocess
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class BlogHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BlogHandler.htdocs_path, **kwargs)

    def guess_type(self, path):
        """Override content type guessing to handle extensionless files."""
        if "." not in os.path.basename(path):
            if self._is_html_content(path):
                return "text/html"
            elif self._is_atom_content(path):
                return "application/rss+xml"
        return super().guess_type(path)

    def _is_html_content(self, path):
        """Check if this extensionless file should be served as HTML."""
        rel_path = os.path.relpath(path, BlogHandler.htdocs_path)

        # Check if it's an article (articles come from www/article/ and get moved to root)
        if "/" in rel_path:  # Has path components like "202505/article-name"
            source_html = os.path.join("www/article", rel_path + ".html")
            if os.path.exists(source_html):
                return True

        # Check if it's a top-level file from www/
        source_html = os.path.join("www", rel_path + ".html")
        return os.path.exists(source_html)

    def _is_atom_content(self, path):
        """Check if this extensionless file should be served as Atom/RSS."""
        rel_path = os.path.relpath(path, BlogHandler.htdocs_path)

        # Check if it's from www/article/ first
        if "/" in rel_path:
            source_atom = os.path.join("www/article", rel_path + ".atom")
            if os.path.exists(source_atom):
                return True

        # Check if it's a top-level file from www/
        source_atom = os.path.join("www", rel_path + ".atom")
        return os.path.exists(source_atom)

    def log_message(self, format, *args):
        """Suppress HTTP request logging to keep output clean."""
        pass


class BlogWatcher(FileSystemEventHandler):
    def __init__(self, server):
        self.server = server
        self.last_build = 0
        self.build_lock = threading.Lock()

    def on_modified(self, event):
        if event.is_directory:
            return

        # Ignore temporary files and non-relevant changes
        if any(pattern in event.src_path for pattern in [".tmp", "~", ".git", "__pycache__"]):
            return

        # Only trigger on files we care about
        path = Path(event.src_path)
        if not (
            path.suffix in [".text", ".conf"] or "conf/" in str(path)
        ):
            return

        # Debounce rapid changes
        now = time.time()
        if now - self.last_build < 1.0:
            return

        with self.build_lock:
            if now - self.last_build < 1.0:  # Double-check after acquiring lock
                return
            self.last_build = now

        print(f"\n🔄 File changed: {event.src_path}")
        self.server.regenerate_content()


class BlogServer:
    def __init__(self, port=8000, auto_reload=False, open_browser=False):
        self.port = port
        self.auto_reload = auto_reload
        self.open_browser = open_browser
        self.temp_dir = None
        self.htdocs_path = None
        self.observer = None
        self.generation_lock = threading.Lock()

    def _run_generator(self):
        """Run the blog generator (equivalent to make update)."""
        print("🔨 Running blog generator...")

        # Ensure feed directory exists
        os.makedirs("www/feed", exist_ok=True)

        # Run the generator from conf directory (like the original does)
        original_cwd = os.getcwd()
        try:
            os.chdir("conf")
            result = subprocess.run(
                ["uv", "run", "python", "-m", "pygen.main"], capture_output=True, text=True, cwd=".."
            )
            if result.returncode != 0:
                print("❌ Generator failed:")
                print(result.stderr)
                return False
            print("✅ Blog generation complete")
            return True
        except Exception as e:
            print(f"❌ Generator error: {e}")
            return False
        finally:
            os.chdir(original_cwd)

    def _setup_content_structure(self):
        """Create the same directory structure as publish.sh."""
        if not self.htdocs_path:
            self.temp_dir = tempfile.mkdtemp(prefix="blog_serve_")
            self.htdocs_path = os.path.join(self.temp_dir, "htdocs")
            BlogHandler.htdocs_path = self.htdocs_path

        # Clean and recreate
        if os.path.exists(self.htdocs_path):
            shutil.rmtree(self.htdocs_path)
        os.makedirs(self.htdocs_path, exist_ok=True)

        print("📁 Setting up production-like structure...")

        # First rsync: copy everything from www/ except /article
        try:
            subprocess.run(
                ["rsync", "-rlp", "--exclude=/article", "www/", f"{self.htdocs_path}/"], check=True, capture_output=True
            )

            # Second rsync: selectively copy from www/article/
            subprocess.run(
                [
                    "rsync",
                    "-rlp",
                    "--include=*.html",
                    "--include=*.png",
                    "--include=*.jpeg",
                    "--include=*.svg",
                    "--include=*.py",
                    "--include=*.zip",
                    "--include=*.cpp",
                    "--include=*/",
                    "--include=**/media/***",
                    "--exclude=*",
                    "www/article/",
                    f"{self.htdocs_path}/",
                ],
                check=True,
                capture_output=True,
            )

            # Apply fixup logic: remove extensions from .html and .atom files
            self._fixup_extensions()
            print("✅ Structure ready")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup structure: {e}")
            return False
        return True

    def _fixup_extensions(self):
        """Remove extensions from .html and .atom files, like publish.sh does."""
        changes = 0
        for ext in ["html", "atom"]:
            for file_path in Path(self.htdocs_path).rglob(f"*.{ext}"):
                # Don't remove extension from index.html - web servers need it
                if file_path.name == "index.html":
                    continue
                new_path = file_path.with_suffix("")
                if not new_path.exists():
                    file_path.rename(new_path)
                    changes += 1
        if changes:
            print(f"📄 Fixed {changes} file extensions")

    def regenerate_content(self):
        """Regenerate blog content and update served structure."""
        with self.generation_lock:
            if self._run_generator():
                if self._setup_content_structure():
                    print("🎉 Content updated successfully")
                else:
                    print("❌ Failed to update structure")
            else:
                print("❌ Failed to regenerate content")

    def _setup_file_watching(self):
        """Set up file system watching for auto-regeneration."""
        self.observer = Observer()
        event_handler = BlogWatcher(self)

        # Watch article source files
        self.observer.schedule(event_handler, "www/article", recursive=True)

        # Watch templates and config
        self.observer.schedule(event_handler, "conf", recursive=True)

        self.observer.start()
        print("👀 Watching for file changes...")
        return True

    def _cleanup(self):
        """Clean up temporary directory and file watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up temporary directory")

    def serve(self):
        """Start the blog development server."""
        try:
            print("🚀 Starting blog development server...")

            # Initial generation
            if not self._run_generator():
                print("❌ Initial generation failed")
                return

            # Setup serving structure
            if not self._setup_content_structure():
                print("❌ Failed to setup serving structure")
                return

            # Setup file watching
            watch_enabled = self._setup_file_watching()

            # Start HTTP server
            server = http.server.HTTPServer(("", self.port), BlogHandler)
            server_url = f"http://localhost:{self.port}"

            print(f"\n🌐 Blog server running at {server_url}")
            print(f"📁 Serving from: {self.htdocs_path}")
            if watch_enabled:
                print("🔄 Auto-regeneration: ENABLED")
            else:
                print("🔄 Auto-regeneration: DISABLED")
            print("\nPress Ctrl+C to stop\n")

            # Open browser if requested
            if self.open_browser:
                threading.Timer(1.0, lambda: webbrowser.open(server_url)).start()

            server.serve_forever()

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self._cleanup()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Blog development server")
    parser.add_argument("port", nargs="?", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--no-watch", action="store_true", help="Disable file watching")
    parser.add_argument("--open", action="store_true", help="Open browser automatically")

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not os.path.exists("www") or not os.path.exists("conf/generator.conf"):
        print("❌ Error: Must be run from the blog root directory")
        return 1

    # Enable file watching unless disabled
    auto_reload = not args.no_watch

    server = BlogServer(args.port, auto_reload, args.open)
    server.serve()
    return 0


if __name__ == "__main__":
    exit(main())
