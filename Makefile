PYTHON ?= python3
PYTHONPATH_VALUE ?= src
PRIOR_ART_ROOT ?= out/prior-art
RESULTS_DIR ?= out/results
XCODE ?= /Applications/Xcode.app
STAGE ?= out/stage
DEVICE ?= iPhone 17 Pro
DOCKER_IMAGE ?= swift:6.3
TARGET ?= arm64-apple-ios26.0-simulator
MIN_VERSION ?= 26.0
SDK_VERSION ?= 26.5
BUNDLE_ID ?= dev.example.IOSLinuxVerificationHarness
XTOOL_TOOLSET_URL ?= https://github.com/xtool-org/darwin-tools-linux-llvm/releases/download/v1.0.1/toolset-aarch64.tar.gz
XCTESTRUN ?=

.PHONY: test audit-prior-art report hygiene verify package-sdk stage-xtool-toolset linux-build mac-verify clean

test:
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

audit-prior-art:
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m ios_linux_harness.cli.audit_prior_art --fetch --prior-art-root "$(PRIOR_ART_ROOT)" --out-dir "$(RESULTS_DIR)"

report:
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m ios_linux_harness.cli.report --prior-art-root "$(PRIOR_ART_ROOT)" --out-dir "$(RESULTS_DIR)"

hygiene:
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m ios_linux_harness.cli.check_hygiene .

verify: test hygiene
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m py_compile src/ios_linux_harness/*.py src/ios_linux_harness/cli/*.py
	bash -n scripts/*.sh
	ruff check . --exclude out --exclude '**/__pycache__'
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m ios_linux_harness.cli.generate_xctestrun --output "$(RESULTS_DIR)/Smoke.xctestrun" --product-module-name AccessibilityProbeUITests --test-bundle-path __TESTROOT__/AccessibilityProbeUITests.xctest --test-host-path __TESTROOT__/XCTRunner.app --ui-target-app-path __TESTROOT__/ExampleApp.app --ui-test
	plutil -lint "$(RESULTS_DIR)/Smoke.xctestrun"
	@tmp_log="$$(mktemp)"; \
	printf '%s\n' 'ACCESSIBILITY_TREE_BEGIN' "StaticText, identifier: 'ProbeBinaryFrameworkValue', label: 'ProbeBinaryKit: 4096'" 'ACCESSIBILITY_TREE_END' > "$$tmp_log"; \
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -m ios_linux_harness.cli.extract_accessibility_tree --log "$$tmp_log" --output "$(RESULTS_DIR)/accessibility-tree-smoke.txt"; \
	test -s "$(RESULTS_DIR)/accessibility-tree-smoke.txt"

package-sdk:
	scripts/package_sdk.sh --xcode "$(XCODE)" --stage "$(STAGE)"

stage-xtool-toolset:
	scripts/stage_xtool_toolset.sh --stage "$(STAGE)" --url "$(XTOOL_TOOLSET_URL)"

linux-build:
	scripts/linux_build.sh --stage "$(STAGE)" --docker-image "$(DOCKER_IMAGE)" --target "$(TARGET)" --min-version "$(MIN_VERSION)" --sdk-version "$(SDK_VERSION)" --bundle-id "$(BUNDLE_ID)"

mac-verify:
	scripts/mac_verify.sh --app "$(STAGE)/build/ExampleApp.app" --device "$(DEVICE)" --result "$(RESULTS_DIR)/verification-report.json" $(if $(XCTESTRUN),--xctestrun "$(XCTESTRUN)",)

clean:
	rm -rf out
