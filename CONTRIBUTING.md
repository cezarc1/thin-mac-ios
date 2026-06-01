# Contributing

This repo is an evidence harness. Contributions should keep claims narrow,
reproducible, and source-backed.

## Local Checks

Run the lightweight publish-readiness gate before opening changes:

```bash
make verify
make audit-prior-art
```

The heavyweight Apple path is intentionally separate:

```bash
make package-sdk XCODE=/Applications/Xcode.app STAGE=out/stage
make stage-xtool-toolset STAGE=out/stage
make linux-build STAGE=out/stage
make mac-verify DEVICE="iPhone 17 Pro"
```

## Artifact Rules

Do not commit Apple SDKs, simulator runtimes, `.app` bundles, `.xctest`
bundles, `.xcresult` bundles, provisioning profiles, signing keys, or
certificates. Generated material belongs under ignored `out/`.

## Claim Rules

Do not claim first discovery of iOS cross-compilation from Linux. The prior-art
audit exists to keep the README and generated reports honest.
