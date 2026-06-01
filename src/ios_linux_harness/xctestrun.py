from __future__ import annotations

import plistlib
from pathlib import Path
from typing import Any


def build_xctestrun_payload(
    *,
    product_module_name: str,
    test_bundle_path: str,
    test_host_path: str,
    ui_target_app_path: str | None,
    is_ui_test: bool,
) -> dict[str, Any]:
    target: dict[str, Any] = {
        "ProductModuleName": product_module_name,
        "TestBundlePath": test_bundle_path,
        "TestHostPath": test_host_path,
        "TestingEnvironmentVariables": {
            "DYLD_FRAMEWORK_PATH": "__TESTROOT__/Frameworks",
            "DYLD_LIBRARY_PATH": "__TESTROOT__/Frameworks",
        },
        "SystemAttachmentLifetime": "keepNever",
        "UserAttachmentLifetime": "keepNever",
    }
    if is_ui_test:
        target["IsUITestBundle"] = True
        if ui_target_app_path is None:
            raise ValueError("ui_target_app_path is required for UI tests")
        target["UITargetAppPath"] = ui_target_app_path
        target["DependentProductPaths"] = [ui_target_app_path, test_bundle_path]
    else:
        target["IsAppHostedTestBundle"] = True
        target["DependentProductPaths"] = [test_host_path, test_bundle_path]

    return {
        "TestConfigurations": [
            {
                "Name": "LinuxGeneratedConfiguration",
                "IsEnabled": True,
                "TestTargets": [target],
            }
        ],
        "__xctestrun_metadata__": {
            "FormatVersion": "2",
            "GeneratedBy": "thin-mac-ios",
        },
    }


def write_xctestrun(
    output: Path,
    *,
    product_module_name: str,
    test_bundle_path: str,
    test_host_path: str,
    ui_target_app_path: str | None,
    is_ui_test: bool,
) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_xctestrun_payload(
        product_module_name=product_module_name,
        test_bundle_path=test_bundle_path,
        test_host_path=test_host_path,
        ui_target_app_path=ui_target_app_path,
        is_ui_test=is_ui_test,
    )
    output.write_bytes(plistlib.dumps(payload, sort_keys=False))
    return output
