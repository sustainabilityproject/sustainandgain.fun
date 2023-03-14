# Background Worker

## Features

- Sends emails to users every day at 12:00 with all new notifications.
- Processes bomb tasks and sends email if they are exploding in less than 2 hours.
- If a bomb task has not been completed by the time it is supposed to explode, it's status is changed to `EXPLODED`.

## Setup

Make sure you have [Rust](https://rustup.rs) and [Docker](https://www.docker.com/) installed.

### Environment Variables

The following environment variables are required:

- `DATABASE_URL` - The URL of the database to connect to
- `EMAIL_HOST` - The host of the SMTP server to use
- `EMAIL_PORT` - The port of the SMTP server to use
- `EMAIL_USE_TLS` - Whether to use TLS for the SMTP connection
- `EMAIL_HOST_USER` - The username to use for the SMTP connection
- `EMAIL_HOST_PASSWORD` - The password to use for the SMTP connection

### Running

In the root directory of the project, run:

```bash
docker compose up
```

This will run a PostgreSQL database and a local mail server.

The default login for Postgres is `sustain` with the password `sustain`.

- `DATABASE_URL='postgres://sustain:sustain@localhost:5432/sustain'`

Run the worker

```bash
cargo run --release
```