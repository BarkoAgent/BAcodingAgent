"""
Python implementations of Claude Code's built-in tools.
"""

import fnmatch
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Literal


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read(file_path: str, offset: int = 0, limit: int = None, _run_test_id='1') -> str:
    """Read a file and return its contents with line numbers (cat -n style). Only allows reading files within ROOT_TEST directory."""
    import os
    from pathlib import Path
    root = os.environ.get('ROOT_TEST')
    if not root:
        raise EnvironmentError('ROOT_TEST environment variable is not set')
    root_path = Path(root).resolve()
    file_path_obj = Path(file_path).resolve()
    if not str(file_path_obj).startswith(str(root_path)):
        raise PermissionError(f"Access denied: {file_path} is not within ROOT_TEST directory")
    if isinstance(offset, str):
        offset = int(offset) if offset else 0
    if isinstance(limit, str):
        limit = int(limit) if limit else None
    with open(file_path, "r") as f:
        lines = f.readlines()

    if offset:
        lines = lines[offset:]
    if limit is not None:
        lines = lines[:limit]

    start = offset + 1
    result = ""
    for i, line in enumerate(lines, start=start):
        result += f"{i:>6}\t{line}"
    return result


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def write(file_path: str, content: str, _run_test_id='1') -> None:
    """Write content to a file, overwriting if it exists. Only allows writing files within ROOT_TEST directory."""
    import os
    from pathlib import Path
    root = os.environ.get('ROOT_TEST')
    if not root:
        raise EnvironmentError('ROOT_TEST environment variable is not set')
    root_path = Path(root).resolve()
    file_path_obj = Path(file_path).resolve()
    if not str(file_path_obj).startswith(str(root_path)):
        raise PermissionError(f"Access denied: {file_path} is not within ROOT_TEST directory")
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

def edit(file_path: str, old_string: str, new_string: str, replace_all: bool = False, _run_test_id='1') -> None:
    """Perform an exact string replacement in a file."""
    if isinstance(replace_all, str):
        replace_all = replace_all.lower() in ("true", "1", "yes")
    with open(file_path, "r") as f:
        content = f.read()

    if not replace_all:
        count = content.count(old_string)
        if count == 0:
            raise ValueError(f"old_string not found in {file_path}")
        if count > 1:
            raise ValueError(
                f"old_string is not unique ({count} occurrences). Provide more context."
            )
        content = content.replace(old_string, new_string, 1)
    else:
        if old_string not in content:
            raise ValueError(f"old_string not found in {file_path}")
        content = content.replace(old_string, new_string)

    with open(file_path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Glob
# ---------------------------------------------------------------------------

def glob(pattern: str, path: str = ".", _run_test_id='1') -> list[str]:
    """Find files matching a glob pattern, sorted by modification time (newest first)."""
    matches = []
    for root, dirs, files in os.walk(path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, path)
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(filename, pattern.split("/")[-1]):
                matches.append(full_path)

    matches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return matches


# ---------------------------------------------------------------------------
# Grep
# ---------------------------------------------------------------------------

def grep(
    pattern: str,
    path: str = ".",
    glob: str = None,
    output_mode: Literal["content", "files_with_matches", "count"] = "files_with_matches",
    case_insensitive: bool = False,
    multiline: bool = False,
    context: int = 0,
    head_limit: int = 0,
    _run_test_id='1',
) -> str:
    """Search file contents using a regex pattern."""
    if isinstance(case_insensitive, str):
        case_insensitive = case_insensitive.lower() in ("true", "1", "yes")
    if isinstance(multiline, str):
        multiline = multiline.lower() in ("true", "1", "yes")
    if isinstance(context, str):
        context = int(context) if context else 0
    if isinstance(head_limit, str):
        head_limit = int(head_limit) if head_limit else 0
    flags = re.MULTILINE if multiline else 0
    if case_insensitive:
        flags |= re.IGNORECASE

    # Collect files to search
    files_to_search = []
    if os.path.isfile(path):
        files_to_search = [path]
    else:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                full_path = os.path.join(root, filename)
                if glob:
                    if not fnmatch.fnmatch(filename, glob):
                        continue
                files_to_search.append(full_path)

    results = []

    for file_path in files_to_search:
        try:
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()
        except (OSError, PermissionError):
            continue

        if output_mode == "files_with_matches":
            if re.search(pattern, content, flags):
                results.append(file_path)
        elif output_mode == "count":
            count = len(re.findall(pattern, content, flags))
            if count:
                results.append(f"{file_path}: {count}")
        elif output_mode == "content":
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if re.search(pattern, line, flags):
                    start = max(0, i - context)
                    end = min(len(lines), i + context + 1)
                    for j in range(start, end):
                        prefix = "--" if j != i else f"{j + 1}:"
                        results.append(f"{file_path}:{prefix}{lines[j]}")

        if head_limit and len(results) >= head_limit:
            results = results[:head_limit]
            break

    return "\n".join(results)


# ---------------------------------------------------------------------------
# Bash
# ---------------------------------------------------------------------------

def bash(command: str, timeout: int = 120_000, _run_test_id='1') -> str:
    """Execute a shell command and return its output."""
    if isinstance(timeout, str):
        timeout = int(timeout) if timeout else 120_000
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout / 1000,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.returncode != 0:
        output += f"\n[exit code: {result.returncode}]"
    return output.strip()


# ---------------------------------------------------------------------------
# WebFetch
# ---------------------------------------------------------------------------

def web_fetch(url: str) -> str:
    """Fetch the content of a URL and return it as text."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# WebSearch
# ---------------------------------------------------------------------------

def web_search(query: str, num_results: int = 5, _run_test_id='1') -> list[dict]:
    """
    Search the web using DuckDuckGo's instant answer API.
    Returns a list of {title, url, snippet} dicts.
    Note: For full search results a third-party API key (e.g. SerpAPI) is needed.
    """
    if isinstance(num_results, str):
        num_results = int(num_results) if num_results else 5
    encoded = urllib.request.quote(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1"
    raw = web_fetch(url)
    data = json.loads(raw)

    results = []
    # Abstract (top answer)
    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", ""),
            "url": data.get("AbstractURL", ""),
            "snippet": data["AbstractText"],
        })
    # Related topics
    for topic in data.get("RelatedTopics", [])[:num_results]:
        if "Text" in topic:
            results.append({
                "title": topic.get("Text", "").split(" - ")[0],
                "url": topic.get("FirstURL", ""),
                "snippet": topic.get("Text", ""),
            })

    return results[:num_results]


# ---------------------------------------------------------------------------
# TodoWrite
# ---------------------------------------------------------------------------

TODO_FILE = os.path.join(os.path.dirname(__file__), ".todos.json")


def todo_write(todos: list[dict], _run_test_id='1') -> None:
    """
    Write the full todo list. Each item should be:
      {"id": str, "content": str, "status": "pending"|"in_progress"|"completed", "priority": "low"|"medium"|"high"}
    """
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def todo_read() -> list[dict]:
    """Read the current todo list."""
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== write ===")
    write("/tmp/claude_tools_test.txt", "hello\nworld\n")

    print("=== read ===")
    print(read("/tmp/claude_tools_test.txt"))

    print("=== edit ===")
    edit("/tmp/claude_tools_test.txt", "world", "claude")
    print(read("/tmp/claude_tools_test.txt"))

    print("=== glob ===")
    print(glob("*.py", path="."))

    print("=== grep ===")
    print(grep("def ", path=__file__, output_mode="content", head_limit=5))

    print("=== bash ===")
    print(bash("echo 'hello from bash'"))

    print("=== todo_write / todo_read ===")
    todo_write([{"id": "1", "content": "demo task", "status": "pending", "priority": "high"}])
    print(todo_read())
