# Runtime Boundary

Linux build success does not imply Linux execution of iOS UI code.

The current runtime ladder is:

```text
Minimal Mach-O CLI
  -> Mach-O segment mapping, LC_MAIN entry, /usr/lib/dyld
  -> Darwin libSystem and chained fixups

Foundation-only Mach-O CLI
  -> Objective-C metadata and selector/class registration
  -> Foundation/CoreFoundation behavior
  -> Darwin Swift runtime libraries

SwiftUI/UIKit app
  -> UIKit and SwiftUI framework behavior
  -> CoreSimulator and SpringBoard service chains
  -> CoreAnimation/IOSurface graphics
  -> event delivery and accessibility surfaces
```

This repo therefore treats Linux-only UIKit execution as research. The
product-shaped path is Linux build capacity plus thin Mac runtime verification.
