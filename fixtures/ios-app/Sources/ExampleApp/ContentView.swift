import ProbeBinaryKit
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 12) {
            Text("Linux-built iOS app")
                .font(.headline)
            Text("ProbeBinaryKit: \(ProbeBinaryKitAnswer())")
                .font(.body.monospacedDigit())
                .accessibilityIdentifier("ProbeBinaryFrameworkValue")
        }
        .padding()
    }
}
