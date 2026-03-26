# One-time: make `docs/contracts/hotmart` a submodule of OrganicEcom

Do this on a branch; coordinate with anyone else touching Hotmart contracts.

## 1. Create an empty remote repository

Create a new repo (e.g. `OrganicEcom-hotmart-postman` or `hotmart-postman-workspace`) on your Git host. **Do not** add a README or license on the host if you want an unrelated histories merge; an empty repo is fine.

## 2. Publish this folder as the first commit of that remote

From **OrganicEcom** root, with the Hotmart files already in `docs/contracts/hotmart`:

```bash
cd docs/contracts/hotmart
git init
git add .
git commit -m "Initial Hotmart Postman workspace export"
git branch -M main
git remote add origin <REMOTE_URL>
git push -u origin main
```

## 3. Replace the tracked folder in OrganicEcom with the submodule

From **OrganicEcom** root (not inside `hotmart`):

```bash
git rm -r --cached docs/contracts/hotmart
rm -rf docs/contracts/hotmart
git submodule add <REMOTE_URL> docs/contracts/hotmart
git submodule update --init --recursive
git add .gitmodules docs/contracts/hotmart
git commit -m "chore: add Hotmart Postman workspace as submodule at docs/contracts/hotmart"
```

Adjust `rm -rf` if you need to preserve untracked files; back up first.

## 4. Verify

- `docs/contracts/hotmart` should be a gitlink (submodule pointer) in the parent repo.
- `git submodule status` shows the submodule commit.
- Paths in `docs/contracts/.postman/resources.yaml` still resolve to `../hotmart/...` from `.postman/`.

## 5. Clones

Document for contributors:

```bash
git clone --recurse-submodules <OrganicEcom-url>
# or after a normal clone:
git submodule update --init --recursive docs/contracts/hotmart
```

## Notes

- Submodule commits are pinned by the parent repo; bump the submodule pointer when you update Postman exports.
- Keep secrets out of Git; environment JSON should keep empty values for credentials and tokens.
