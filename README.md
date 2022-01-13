# Github Release Discord Bot

A discord bot to watch a collection of Github repositories and notify
a channel when a new release is published.

## Installation

```sh
$ git clone https://github.com/blockjoe/release_watch.git
cd release_watch
pip install .
```

## Configuration

There are two parts that need configuration depending on your needs.

1) The Github and Discord Access Tokens
2) The desired list of repositories to watch

### The Access Tokens

This bot needs some form of basic Github Authentication. Currently it is setup
to utilize a personal access token with no scope.  Details on that process
[here](https://docs.github.com/en/articles/creating-an-access-token-for-command-line-use).


The bot also needs to be able to connect to a registered discord bot account.
This discord bot needs the bot scope, and it needs permissions to send messages
and embed links. Instructions for setting up a bot account can be found
[here](https://discordpy.readthedocs.io/en/stable/discord.html). Once a bot is
configured and added to the server, it's Token, which can be found under the
bot tab of the [developer portal](https://discord.com/developers/applications)
is needed.

Once you have these values, create an `.env` file from the example in the root of
the project:

```sh
$ cp .env.example .env
```

Then open the `.env` file, `GH_USERNAME` is the username that the token was registered to,
`GH_TOKEN` is the access token for GitHub that was created earlier, and `DISCORD_TOKEN` is
the token of the bot account.

You can also set these as environment variables if you wish.


### The Repository Configuration File

By default the configuration of the repositories to watch can be found in `repos.yml`.
Each entry is formatted as follows:

```yaml
name:
  channel: id-of-the-discord-channel-to-notify
  repo: url-to-the-repo
  critical: true/false # If False, notifications won't be sent. Set to True to get notifications.
```

To get the channel id, navigate in discord to the channel that you wish to notify. The channel id can
by found from the URL as follows: `discord.com/channels/<long-number>/<channel-id>`

The repo url should be the base URL to the GitHub repository.

Critical should be set to true if you want notifications. This value is here so
that notifications can be toggled on as needed.

## Running

To start the bot, simply run.

```sh
$ relase_watch
```

Full details:

```sh
$ release_watch -h
usage: release_watch [-h] [-t TIME] [-c CONFIG]

Discord bot for watching for unannouced github releases.

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  How often, in seconds, to check each of the tracked
                        repositories.
  -c CONFIG, --config CONFIG
                        The path to the repos configuration file. The default
                        path for this is repos.yml in the root of the project.
```
