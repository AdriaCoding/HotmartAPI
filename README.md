# Hotmart — Postman workspace (Git submodule)

This directory is intended to be its **own Git repository** and is linked into **OrganicEcom** as a **submodule** at `docs/contracts/hotmart`.

## Contents

| File | Role |
|------|------|
| `Hotmart API — OrganicEcom.postman_collection.json` | Postman Collection v2.1 (import or used by Postman CLI / local workspace) |
| `Hotmart — OrganicEcom.postman_environment.json` | Postman environment (variables; secrets stay empty in Git) |
| `workspace.meta.yaml` | Workspace / cloud IDs for traceability |
| `hotmart-docs-crawl/` | Optional scripts to refresh generated requests from Hotmart docs |

Parent repo also keeps:

- `docs/contracts/.postman/resources.yaml` — binds this folder’s JSON + `hotmart.openapi.yaml` to a Postman workspace.
- `docs/contracts/postman/` — optional YAML representation of the collection for Postman’s Git integration.

## Cloning OrganicEcom with this submodule

From the OrganicEcom root:

```bash
git submodule update --init --recursive docs/contracts/hotmart
```

Or clone with submodules:

```bash
git clone --recurse-submodules <OrganicEcom-url>
```

## Working only in this repo

After `git clone` of **this** repository alone, open Postman and import the collection + environment JSON, or point your Postman local workspace at the parent `docs/contracts/.postman` layout if you have the full contracts tree.

## Submodule setup (maintainers)

See [SUBMODULE_SETUP.md](SUBMODULE_SETUP.md) for turning this folder into a submodule of OrganicEcom (one-time migration).
