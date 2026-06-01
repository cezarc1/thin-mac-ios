# Security

This repository should never contain private Apple or tenant material.

Do not commit:

- App Store Connect `.p8` keys
- certificates or `.p12` files
- provisioning profiles
- Apple SDKs or simulator runtimes
- built `.app`, `.ipa`, `.xctest`, or `.xcresult` artifacts

The hygiene command checks tracked files for common mistakes:

```bash
make hygiene
```

If sensitive material is committed, rotate the credential and rewrite the
public history before publishing.
