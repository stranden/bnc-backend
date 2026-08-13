# Broadcast Network Controller (BNC)

Backend for Broadcast Network Controller (BNC), built with FastAPI and
[NetBox](https://netbox.dev). NetBox remains the single source of truth; BNC
does not persist a separate copy of NetBox objects.

The current implementation provides a NetBox client and low-level
`pynetbox` adapter for BNC-tagged VLAN Groups, VLANs, prefixes, and IP ranges.
Read operations require the external-control tag. Create and update operations
also require the state-management tag, so writes are limited to objects that
are explicitly managed by BNC.

The FastAPI application is currently scaffolded and does not register HTTP
routes yet. Network-profile definitions are available for `data`, `dante`,
`aes67`, and `smpte-2110`.

## Configuration

All settings are environment variables (see `.env.example`). Key ones:

| Variable                    | Description                                             |
|-----------------------------|---------------------------------------------------------|
| `NETBOX_URL`                | Base URL of the NetBox instance                         |
| `NETBOX_TOKEN`              | NetBox API token                                        |
| `NETBOX_TAG_EXTERNAL_CTRL`  | Slug of the tag BNC is scoped to (default: `external-ctrl-bnc`) |
| `NETBOX_TAG_STATE_MANAGE`   | Slug of the tag that permits BNC-managed writes (default: `bnc-state-manage`) |
| `NETBOX_VERIFY_SSL`         | Verify NetBox's TLS certificate                         |

Copy `.env.example` to `.env` for local development, or pass variables via
`docker run -e ...` / `docker-compose.yml` in production.

## Running

```bash
docker compose up --build
```

The FastAPI application will be available at `http://localhost:8000`.
Interactive OpenAPI documentation is available at `/docs`.

For local development without Docker, install the dependencies and start
Uvicorn from the repository root:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

