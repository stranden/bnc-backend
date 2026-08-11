# bnc-backend
Backend for Broadcast Network Controller (BNC)

FastAPI service that reads Sites, Devices, Device Types, Prefixes, IP
Addresses, VLAN Groups and VLANs from [NetBox](https://netbox.dev), scoped
strictly to objects tagged with a configurable BNC tag (default slug
`external-ctrl-bnc`, corresponding to a NetBox tag such as `external-ctrl:
bnc`). NetBox remains the single source of truth (SSoT/NSoT) — BNC does not
persist its own copy of these objects.

A second, stricter tag (default slug `bnc-state-manage`, corresponding to a
NetBox tag such as `bnc-state: manage`) marks devices that BNC is
additionally allowed to *actively manage* — e.g. changing switch ports or
pushing configuration. A device must carry both tags before any future
write/push operation will be permitted against it (`NetBoxClient.
require_manageable_device`); read-only sync only requires the first tag.

A NetBox webhook receiver (`POST /webhooks/netbox`) is scaffolded to receive
change events for BNC-tagged objects; the push-to-network step (via Nornir +
NAPALM) will be wired in as a follow-up once the read path is stable.

## Configuration

All settings are environment variables (see `.env.example`). Key ones:

| Variable                | Description                                             |
|-------------------------|-----------------------------------------------------------|
| `NETBOX_URL`            | Base URL of the NetBox instance                          |
| `NETBOX_TOKEN`          | NetBox API token                                         |
| `NETBOX_SYNC_TAG`       | Slug of the tag BNC is scoped to (e.g. `external-ctrl-bnc`) |
| `NETBOX_MANAGE_TAG`     | Slug of the tag marking devices BNC may actively manage (e.g. `bnc-state-manage`) |
| `NETBOX_VERIFY_SSL`     | Verify NetBox's TLS certificate                          |
| `NETBOX_WEBHOOK_SECRET` | Shared secret for verifying NetBox webhook signatures    |

Copy `.env.example` to `.env` for local development, or pass variables via
`docker run -e ...` / `docker-compose.yml` in production.

## Running

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000` (interactive docs at
`/docs`).

