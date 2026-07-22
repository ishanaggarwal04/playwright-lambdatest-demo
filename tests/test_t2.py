from playwright.sync_api import expect


def test_dynamic_counter(page):

    page.goto("http://localhost:3000")

    counter = page.locator("#counter")
    increment_button = page.locator("#increment")

    # Verify the initial value
    expect(counter).to_have_text("0")

    # Click the button 5 times and verify after each click
    for expected_value in range(1, 6):
        increment_button.click()
        expect(counter).to_have_text(str(expected_value))