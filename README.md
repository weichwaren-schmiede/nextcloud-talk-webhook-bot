# nextcloud-talk-webhook-bot

A lightweight FastAPI wrapper that accepts webhook payloads and forwards them to a Nextcloud Talk bot. It is ideal for bridging other systems (CI/CD, monitoring, home automation, etc.) with Nextcloud Talk without having to write custom bot logic.

## Features
- Validates Nextcloud credentials (`NC_URL`, `TOKEN`, `SECRET`) and signs every request using the Talk bot HMAC headers.
- Exposes a simple `/send_message` HTTP endpoint that accepts a `message` field.
- Designed to be run via Docker, `uvicorn`, or any ASGI server.
- Offers ready-made support for [Shoutrr](https://github.com/containrrr/shoutrrr) generic webhooks so you can push notifications from ton of integrations.

## Getting started
1. Copy `compose.example.yml` to `compose.yml` (or set the environment variables manually).
2. Provide the following configuration:
   ```dotenv
   NC_URL=https://your.nextcloud.instance
   TOKEN=xxxxxx-your-talk-bot-token
   SECRET=shared-webhook-secret
   ```
3. Run the API locally with `uvicorn`:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
   Or build and start the Docker image:
   ```bash
   docker build -t nextcloud-talk-webhook-bot .
   docker run -e NC_URL=... -e TOKEN=... -e SECRET=... -p 8000:80 nextcloud-talk-webhook-bot
   ```
   Or use Docker Compose:
   ```bash
    docker compose up -d --build
    ```

## Using `/send_message`
Send a POST request with JSON body:
```json
{
  "message": "Notification body"
}
```

## Example Shoutrr generic webhook integration
1. Beszel (https://beszel.dev/guide/notifications/) already ships with a Shoutrr workflow that posts to this bot via `generic://localhost:81/send_message?template=json`, so you can plug this bot straight into that guide without extra formatting steps.

## Troubleshooting & tips
- Verify `NC_URL`, `TOKEN`, and `SECRET` are reachable/error-free via logs printed by the bot.
- Look at the Nextcloud Talk bot response to catch HTTP errors (`response.json()` is logged).
- Enable verbose logging in Docker (e.g., `docker logs -f <container>`) or the terminal running `uvicorn`.
- When running behind proxies, expose `--proxy-headers` in the Docker command and keep `SECRET` strong and unique.
