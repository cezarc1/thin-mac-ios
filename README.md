# thin-mac-ios

How far can iOS build and verification work move off Macs?

This repo is a small research harness for a hybrid answer: build
iOS-simulator-shaped artifacts on Linux, then use macOS only for the runtime
pieces that still require CoreSimulator.

It is deliberately not a victory lap. Linux-to-iOS cross-compilation has prior
art. UIKit does not run on Linux here. Macs are still required for simulator
launch, screenshots, accessibility capture, and real UI verification.

## What This Tests

```text
Linux: build the app/framework artifacts
Mac: install, launch, screenshot, capture accessibility, optionally run tests
```

The useful question is not "can Linux replace every Mac?" It is:

```text
Can the Mac become a thin, scarce runtime verifier instead of the whole build box?
```

## Current Evidence

The harness contains:

- a minimal SwiftUI iOS app fixture
- a small embedded C framework used as runtime proof
- Linux build scripts for staged Apple SDK and xtool linker inputs
- Mac verification scripts for CoreSimulator install/launch/capture
- a prior-art audit that prevents broad novelty claims

The audit currently leaves only narrow candidate deltas:

- screenshot plus accessibility tree from a Linux-built app
- Linux-built binary framework evidence visible at runtime
- a runtime-boundary map for why UIKit-on-Linux remains research

## Non-Claims

This repo does not claim:

- iOS cross-compilation from Linux is new
- Linux-built `.app` bundles are new
- `.xctestrun` handoff to macOS is new
- UIKit runs on Linux
- Macs are no longer needed for iOS verification

## Quick Start

Run the lightweight public checks:

```bash
make verify
make audit-prior-art
```

Reports land under ignored `out/results/novelty-matrix.{md,json}`.

## Full Local Reproduction

The heavier path requires Xcode, Docker, and the xtool Darwin linker toolset.
Apple SDKs, app bundles, test bundles, and signing material stay local and are
ignored by git.

```bash
make package-sdk XCODE=/Applications/Xcode.app STAGE=out/stage
make stage-xtool-toolset STAGE=out/stage
make linux-build STAGE=out/stage
make mac-verify DEVICE="iPhone 17 Pro"
```

`linux-build` currently builds the sample app and embedded framework. The test
sources under `fixtures/ios-app/Tests` document the verification surface; full
test-bundle compilation is intentionally left as a next step.

## Repo Layout

```text
src/ios_linux_harness/   Python package and CLI entry points
fixtures/ios-app/        SwiftUI app, C framework, and iOS test fixtures
scripts/                 Apple/Docker-heavy workflow wrappers
docs/                    Prior art, publishing, and runtime-boundary notes
tests/                   Python tests for claims and command contracts
out/                     Ignored generated artifacts
```

## Read Before Publishing

Read [prior art](docs/prior-art.md), [runtime boundary](docs/runtime-boundary.md),
and [publishing](docs/publishing.md) before making public claims.

License: MIT.
