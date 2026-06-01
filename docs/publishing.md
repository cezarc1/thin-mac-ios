# Publishing

Publish this repo only when the generated prior-art audit leaves at least two
candidate deltas:

```bash
make verify
make audit-prior-art
```

The audit writes:

```text
out/results/novelty-matrix.md
out/results/novelty-matrix.json
```

Release checklist:

- README says what is not novel before saying what is interesting.
- `make verify` passes.
- `make audit-prior-art` passes.
- `make hygiene` reports clean tracked files.
- No Apple SDKs, simulator runtimes, signing keys, provisioning profiles, or
  generated app/test artifacts are tracked.
- Heavyweight Apple/Docker commands are documented as local-only reproduction
  steps, not required for the lightweight gate.

If the audit gate fails, publish only a writeup. Do not publish code with
novelty language.
