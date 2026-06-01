# Prior Art

This repository should be published only with conservative claims.

Known prior art includes:

- `apple-cross-toolchain/rules_applecross`
- `apple-cross-toolchain/xctestrunner-bash`
- `xtool-org/xtool`
- `kabiroberai/linux-app`

The audit intentionally marks broad Linux-to-iOS build surfaces as not novel.
It also marks `.xctestrun` / UI-test handoff to macOS as not novel because
`rules_applecross` and `xctestrunner-bash` already expose comparable machinery.

Run:

```bash
make audit-prior-art
```

Current candidate deltas are narrower:

- visual screenshot plus accessibility tree from a Linux-built app
- Linux-built binary framework evidence visible through runtime/UI surfaces
- runtime-substrate ladder explaining why UIKit-on-Linux remains research

Swift Testing remains a useful fixture, but the source-pattern audit does not
treat it as a safe standalone novelty claim.
