# Gunnersaurus, a Discord Bot.

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.
* A Discord [Bot token](https://discord.com/developers/applications)

## Docker Compose

Once you have configured a BOT Token inside of a `.env` (`TOKEN=<token>`), you can start the bot with Docker Compose

```console
$ docker compose watch
```

## UV

Or, with UV. The dependencies are managed with [uv](https://docs.astral.sh/uv/).

You can then install all the dependencies with:

```console
$ uv sync
```

You can then activate the virtual environment with:

```console
$ source .venv/bin/activate
```
Then start the bot with:

```console
$ python -m bot.py
```
