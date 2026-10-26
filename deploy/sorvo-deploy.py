#!/usr/bin/python3
"""Publish public/main as static files; never execute repository code."""
import fcntl, io, os, pathlib, subprocess, tarfile, tempfile
BASE = pathlib.Path("/var/www/sorvo-auto")
STATE = pathlib.Path("/var/lib/sorvo-deploy")
REPO = STATE / "repo.git"
URL = "https://github.com/SorvoStudio/sorvo-studio-website.git"
def git(*args):
    return subprocess.check_output(["git", "-c", "core.hooksPath=/dev/null", "--git-dir=" + str(REPO), *args], timeout=90)
with (STATE / "lock").open("w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if not REPO.exists():
        subprocess.run(["git", "init", "--bare", str(REPO)], check=True, timeout=30)
    git("fetch", "--depth=1", "--no-tags", URL, "+refs/heads/main:refs/heads/main")
    sha = git("rev-parse", "refs/heads/main").decode().strip()
    current = BASE / "current"
    if current.is_symlink() and current.resolve().parent.name == sha:
        print("Unchanged " + sha)
        raise SystemExit(0)
    archive = git("archive", "--format=tar", sha, "public")
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        members = tf.getmembers()
        for m in members:
            p = pathlib.PurePosixPath(m.name)
            if p.is_absolute() or ".." in p.parts or p.parts[0] != "public" or not (m.isfile() or m.isdir()):
                raise RuntimeError("Unsafe public file: " + m.name)
        with tempfile.TemporaryDirectory(prefix="staging-", dir=BASE) as tmp:
            tf.extractall(tmp, members=members)
            root = pathlib.Path(tmp) / "public"
            for name in ("index.html", "privacy.html", "app-ads.txt", "style.css", "script.js", "logo.png", "favicon.ico"):
                if not (root / name).is_file() or (root / name).stat().st_size == 0:
                    raise RuntimeError("Missing/empty required file: " + name)
            for p in pathlib.Path(tmp).rglob("*"):
                p.chmod(0o755 if p.is_dir() else 0o644)
            # Public version marker enables checking which GitHub commit is live.
            (root / "deployment-version.txt").write_text(sha + "\n")
            release = BASE / "releases" / sha
            if not release.exists():
                release.mkdir(mode=0o755)
                root.rename(release / "public")
    pending = BASE / "current.next"
    if pending.is_symlink():
        pending.unlink()
    pending.symlink_to(release / "public")
    os.replace(pending, current)
    print("Published " + sha, flush=True)
