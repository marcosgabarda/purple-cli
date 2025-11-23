# purple-cli

`purple-cli` is a tool to retrieve information from Twitch, in a format that can be 
used to integrate with other scripts or applications.

It requires to have an application created in Twitch, with a client id and a client 
secret that will be use to obtain the necessary credentials.

## Settings

This tool requires the following environment variables to work:

- `PURPLE_CLIENT_ID` Twitch application client id.
- `PURPLE_CLIENT_SECRET` Twitch application client secret.
