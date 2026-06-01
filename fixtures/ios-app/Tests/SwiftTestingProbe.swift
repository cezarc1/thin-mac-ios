import Testing
import UIKit

@Test
func swiftTestingBundleCanUseIOSRuntimeTypes() {
    #expect(UIView().isUserInteractionEnabled)
}
