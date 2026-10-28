# Security policy

## Reporting a vulnerability

Please don't open a public issue for security problems. Report them privately
instead: go to the **Security** tab of this repo and click **Report a
vulnerability**. Only the maintainer can see the report.

## Scope

tasks-api is a single-user API meant to run only on your own machine
(`127.0.0.1`). It has no login, so don't expose it to a network, for example
by starting uvicorn with `--host 0.0.0.0`.
