# purple-cli

`purple-cli` is a tool to retrieve information from Twitch, in a format that can be 
used to integrate with other scripts or applications.

It requires to have an application created in Twitch, with a client id and a client 
secret that will be use to obtain the necessary credentials.

## Install

The recommended way to install purple is using [pipx](https://pipx.pypa.io/latest/installation/).
This could be done by using directly the repository URL:

```bash
pipx install git+https://tangled.org/mgabarda.com/purple-cli
```

This will add `purple` command to your shell:

```bash
$ purple -h
usage: purple [-h] [-v] [-V] [--popular [POPULAR]] [-l [LANG]]

Get the list of live streams from the list of following channels in Twitch.

options:
  -h, --help           show this help message and exit
  -v, --verbose        increase output verbosity
  -V, --version        show version
  --popular [POPULAR]  get the list of live streams with most viewers (top 20 by default).
  -l, --lang [LANG]    filter the list of live streams by language.
```

## Settings

`purple-cli` requires uses a [Twitch application](https://dev.twitch.tv/console/apps/create),
and to take from there the credentials. 

The following environment variables can be used to set the credentials:

- `PURPLE_CLIENT_ID` Twitch application client id.
- `PURPLE_CLIENT_SECRET` Twitch application client secret.
