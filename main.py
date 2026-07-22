import json
import os
import urllib.parse

import pytest
from playwright.sync_api import sync_playwright


# Mapping between Playwright browsers and LambdaTest browser names
BROWSERS = {
    "chromium": "pw-chromium",
    "firefox": "pw-firefox",
    "webkit": "pw-webkit",
}


@pytest.fixture(params=BROWSERS.keys())
def page(request):
    """
    Creates a remote Playwright browser session on LambdaTest.
    Runs each test once on Chromium, Firefox and WebKit.
    """

    username = os.getenv("LT_USERNAME")
    access_key = os.getenv("LT_ACCESS_KEY")

    if not username or not access_key:
        raise ValueError(
            "LT_USERNAME and LT_ACCESS_KEY environment variables are not set."
        )

    playwright_browser = request.param
    lt_browser = BROWSERS[playwright_browser]

    capabilities = {
        "browserName": lt_browser,
        "browserVersion": "latest",
        "LT:Options": {
            "platform": "Windows 10",
            "build": "Playwright Demo Build",
            "project": "Playwright Demo",
            "name": request.node.nodeid,
            "user": username,
            "accessKey": access_key,
            "video": True,
            "network": True,
            "console": True,
            "tunnel": True,
        },
    }

    ws_endpoint = (
        "wss://cdp.lambdatest.com/playwright"
        "?capabilities="
        + urllib.parse.quote(json.dumps(capabilities))
    )

    print(f"\nConnecting to LambdaTest using {playwright_browser}...")

    with sync_playwright() as p:

        # Always connect using the Chromium client.
        # LambdaTest launches the browser specified in browserName.
        browser = p.chromium.connect(ws_endpoint)

        context = browser.new_context()

        page = context.new_page()

        yield page

        context.close()
        browser.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Update LambdaTest session status after every test.
    """

    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    page = item.funcargs.get("page")

    if page is None:
        return

    status = "passed" if report.passed else "failed"

    remark = (
        "Test Passed"
        if report.passed
        else str(report.longrepr)[:250]
    )

    page.evaluate(
        "_ => {}",
        f"lambdatest_action: {json.dumps({
            'action': 'setTestStatus',
            'arguments': {
                'status': status,
                'remark': remark
            }
        })}",
    )