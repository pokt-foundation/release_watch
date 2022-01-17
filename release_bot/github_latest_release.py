from dataclasses import dataclass
import datetime
from functools import lru_cache
import os.path
import urllib.parse

GITHUB_HEADERS : dict = {"Accept": "application/vnd.github.v3+json"}
GITHUB_LATEST_RELEASE_FORMAT_STR : str = "https://api.github.com/repos/{owner}/{repo}/releases/latest"

@dataclass
class GithubReleaseInfo:
    html_url: str
    release_id: int
    tag: str
    name: str
    body: str
    is_draft: bool
    is_prerelease: bool
    published_date: datetime.datetime

@lru_cache(maxsize=None)
def _github_repo_url_to_latest_release_api_url(repo_url : str) -> str:
    url_parts = urllib.parse.urlsplit(repo_url)
    if url_parts.netloc != "github.com":
        raise ValueError("This method only supports Github URLS, got {}".format(url_parts.netloc))
    path_parts = os.path.split(url_parts.path)
    if len(path_parts) != 2:
        raise ValueError("The provided url, {}, does not appear to point to a repository.".format(repo_url))
    owner, repo = path_parts
    owner = owner.replace("/", "")
    return GITHUB_LATEST_RELEASE_FORMAT_STR.format(owner=owner, repo=repo)

def _parse_github_release_info(release_data : dict) -> GithubReleaseInfo:
    published_at = release_data["published_at"].replace('Z', '+00:00')
    published_date = datetime.datetime.fromisoformat(published_at)
    return GithubReleaseInfo(
        html_url=release_data["html_url"],
        release_id=release_data["id"],
        tag=release_data["tag_name"],
        name=release_data["name"],
        is_draft=release_data["draft"],
        is_prerelease=release_data["prerelease"],
        body=release_data["body"],
        published_date=published_date
    )

async def get_latest_release(repo_url : str, session) -> GithubReleaseInfo:
    """
    Get the latests github release for a given repo url

    Parameters
    ----------
    repo_url: str
        The URL to the base of the github repository

    Returns
    -------
    GithubReleaseInfo
    """
    api_url = _github_repo_url_to_latest_release_api_url(repo_url)
    async with session.get(api_url, headers=GITHUB_HEADERS) as release_resp:
        if release_resp.status != 200:
            raise RuntimeError("Non-successful release response")
        release_data = await release_resp.json()
        return _parse_github_release_info(release_data)
