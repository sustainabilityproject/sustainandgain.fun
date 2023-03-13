# Background Worker

A background worker which checks for new notifications and sends them to the user via email.

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