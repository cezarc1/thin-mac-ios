import XCTest

final class AccessibilityProbeUITests: XCTestCase {
    func testBinaryFrameworkValueIsVisible() throws {
        let app = XCUIApplication()
        app.launch()

        let value = app.staticTexts["ProbeBinaryFrameworkValue"]
        XCTAssertTrue(value.waitForExistence(timeout: 10))
        XCTAssertEqual(value.label, "ProbeBinaryKit: 4096")

        print("ACCESSIBILITY_TREE_BEGIN")
        print(app.debugDescription)
        print("ACCESSIBILITY_TREE_END")
    }
}
