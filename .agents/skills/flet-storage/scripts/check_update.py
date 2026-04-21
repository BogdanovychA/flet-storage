import io
import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)


def get_remote_content(repo_url: str) -> str | None:
    """Fetches content from a remote URL."""
    try:
        with urllib.request.urlopen(repo_url, timeout=5) as response:
            content = response.read().decode('utf-8')
            return content
    except Exception as e:
        logger.error(f"Error getting remote content: {e}")
        return None


def get_local_content() -> str | None:
    """Reads content from the local SKILL.md file."""
    try:
        base_dir = Path(__file__).resolve().parent.parent
        skill_path = base_dir / "SKILL.md"

        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        logger.error(f"Error getting local content: {e}")
        return None


def read_source(source: io.StringIO) -> dict[str, str]:
    """Parses metadata header from a Markdown source."""
    result = {}
    first_line = next(source, None)

    while first_line is not None and not first_line.strip():
        first_line = next(source, None)

    if first_line is None or first_line.strip() != "---":
        return result

    for line in source:
        line = line.strip()
        if line == "---":
            break

        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


def get_owner_and_repo(repository: str) -> tuple[str | None, str | None]:
    """Extracts owner and repository name from a GitHub URL."""
    suffix = repository.removeprefix("https://github.com/")
    parts = suffix.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


def is_newer_version(remote_v: str, local_v: str) -> bool:
    """Compares two semantic version strings."""
    try:
        remote_parts = [int(p) for p in remote_v.split('.')]
        local_parts = [int(p) for p in local_v.split('.')]
        return remote_parts > local_parts
    except (ValueError, AttributeError):
        return remote_v > local_v


def main() -> None:
    """Main function to check for skill updates."""

    local_content = get_local_content()
    if not local_content:
        print("Could not read local SKILL.md.")
        return

    local_data = read_source(io.StringIO(local_content))
    if not local_data:
        print("Could not retrieve local data from SKILL.md.")
        return

    try:
        local_version = local_data["version"]
        repository = local_data["repository"]
        skill_name = local_data["name"]
    except KeyError:
        print("Could not retrieve local data from SKILL.md.")
        return

    owner, repo = get_owner_and_repo(repository)
    if not owner or not repo:
        print(f"Could not parse repository URL: {repository}")
        return

    repo_raw = f"https://raw.githubusercontent.com/{owner}/{repo}/main/.agents/skills/{skill_name}/SKILL.md"

    remote_content = get_remote_content(repo_raw)
    if not remote_content:
        print("Could not retrieve remote SKILL.md. Check your internet connection.")
        return

    remote_data = read_source(io.StringIO(remote_content))
    if not remote_data:
        print("Could not retrieve remote data from SKILL.md.")
        return

    try:
        remote_version = remote_data["version"]
        repository = remote_data["repository"]
        skill_name = remote_data["name"]
    except KeyError:
        print("Could not retrieve remote data from SKILL.md.")
        return

    owner, repo = get_owner_and_repo(repository)
    if not owner or not repo:
        print(f"Could not parse repository URL: {repository}")
        return

    if is_newer_version(remote_version, local_version):
        print(f"UPDATE_AVAILABLE: {remote_version} (current: {local_version})")
        print(f"UPDATE_COMMAND: npx skills update {owner}/{repo} --skill {skill_name}")
        exit(1)
    else:
        print(f"Skill is up to date (version {local_version}).")
        exit(0)


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    main()
