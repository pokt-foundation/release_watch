import argparse
import asyncio
from dataclasses import dataclass
import datetime
from typing import Optional
import os
import os.path

import aiohttp
import discord
from discord.ext.tasks import loop
from dotenv import load_dotenv
import humanize
import yaml

from .github_latest_release import get_latest_release, GithubReleaseInfo

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_REPOS_FILE = os.path.join(ROOT, 'repos.yml')

discord_client = discord.Client()

@dataclass
class RepoConfig:
    chain: str
    channel: int
    critical: bool
    repo: str


def read_repos(repos_file : Optional[str] = None) -> list[RepoConfig]:
    """
    Parse the repos.yml file into a list of RepoConfig objects.

    Parameters
    ----------
    repos_file: str, optional
        Path to the repos config file, defaults to repos.yml in the root.

    Returns
    -------
    list[RepoConfig]
    """
    if not repos_file:
        repos_file = DEFAULT_REPOS_FILE
    with open(repos_file, 'r') as rf:
        repos = yaml.load(rf, Loader=yaml.SafeLoader)
    return [RepoConfig(chain=chain, **config) for chain, config in repos.items()]

def get_session_auth() -> aiohttp.BasicAuth:
    """
    Get the authentication object that aiohttp session from the .env values

    Returns
    -------
    aiohttp.BasicAuth

    Rasies
    ------
    RuntimeError: If either the Github username or Auth token are not provided
    """
    if not os.environ.get("GH_USERNAME"):
        raise RuntimeError("Github usename not configured in .env")
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("Github token not configured in .env")

    return aiohttp.BasicAuth(os.environ.get("GH_USERNAME"), os.environ.get("GH_TOKEN"))

def get_discord_auth() -> str:
    """
    Get the discord auth token from the .env value

    Returns
    -------
    str

    Raises
    ------
    RuntimeError: If the discord token is not provided
    """
    if not os.environ.get("DISCORD_TOKEN"):
        raise RuntimeError("Discord token not configured in .env")
    return os.environ.get("DISCORD_TOKEN")


def format_release_message(chain : str, release_info : GithubReleaseInfo) -> discord.Embed:
    """
    Generate the message to be sent to discord

    Parameters
    ----------
    chain: str
        The name of the chain
    release_info: GithubReleaseInfo
        The object constructed from the release info

    Returns
    -------
    discord.Embed
        An object that represents a formatted discord embed link
    """
    title = "New {} Release - {}".format(chain.title(), release_info.name)
    time_since = datetime.datetime.utcnow() - release_info.published_date.replace(tzinfo=None)
    description = "Published {}, with tag: {}\n\n{}".format(humanize.naturaltime(time_since), release_info.tag, release_info.body)
    message = discord.Embed(title=title, url=release_info.html_url, description=description)
    return message

async def send_message(client : discord.Client, content : discord.Embed, channel_id : int):
    """
    Send the given embed content to the specified channel.

    Parameters
    ----------
    client: discord.Client
    content: discord.Embed
    channel_id: int
        The id of the channel. This is the trailing part of the URL when in the desired channel.
    """
    channel = client.get_channel(channel_id)
    if channel is None:
        raise RuntimeError("The channel with id {} is unaccessible".format(channel_id))
    await channel.send(embed=content)

async def watch_for_release(repo: RepoConfig, wait_after: float, session : aiohttp.ClientSession, dc : discord.Client):
    """
    repo: RepoConfig
    wait_after: float
        How many seconds to wait after call is made.
    session: aiohttp.ClientSession
    dc: discord.Client
    """
    try:
        release = await get_latest_release(repo.repo, session)
    except RuntimeError:
        print("No latest release for {}".format(repo.chain))
    else:
        if release.published_date.replace(tzinfo=None) > datetime.datetime.utcnow():
            message = format_release_message(repo.chain, release)
            await send_message(dc, message, repo.channel)
    finally:
        await asyncio.sleep(wait_after)

@loop()
async def watch_repos():
    """
    Main loop
    """
    args = get_args()
    auth = get_session_auth()
    async with aiohttp.ClientSession(auth=auth) as gh_session:
        repo_configs = read_repos(args.config)
        to_watch = [repo for repo in repo_configs if repo.critical]
        while True:
            for repo in to_watch:
                await watch_for_release(repo, args.time/len(to_watch), gh_session, discord_client)

@discord_client.event
async def on_ready():
    """Start the main loop when the bot is ready"""
    watch_repos.start()

def get_args():
    """argparser dependecny"""
    parser = argparse.ArgumentParser(description="Discord bot for watching for unannouced github releases.")
    parser.add_argument('-t', '--time', default=60, type=float, help="How often, in seconds, to check each of the tracked repositories.")
    parser.add_argument('-c', '--config', default=None, help="The path to the repos configuration file. The default path for this is repos.yml in the root of the project.")
    return parser.parse_args()

def main():
    get_args()
    load_dotenv()
    discord_token = get_discord_auth()
    discord_client.run(discord_token)

if __name__ == "__main__":
    main()
