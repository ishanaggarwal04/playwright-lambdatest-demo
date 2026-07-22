import os

from playwright.sync_api import expect


def test_resume_upload(page):

    filename = "resume.txt"

    with open(filename, "w") as file:
        file.write("This file was uploaded using Playwright.")

    try:
        page.goto("http://localhost:3000")

        file_input = page.locator("#resume")

        file_input.set_input_files(filename)

        expect(file_input).to_have_value("C:\\fakepath\\resume.txt")

    finally:
        if os.path.exists(filename):
            os.remove(filename)