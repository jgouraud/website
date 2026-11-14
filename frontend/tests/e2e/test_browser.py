"""Opt-in real-browser smoke tests of the critical portfolio flows.

Run the server, install Playwright plus Chromium, then set RUN_E2E=1.
They are opt-in because the browser and server are external test dependencies.
"""

import os
import re

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get('RUN_E2E') != '1', reason='Set RUN_E2E=1 with the frontend server running'
)


@pytest.fixture(scope='module')
def page():
    playwright_module = pytest.importorskip('playwright.sync_api')
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        browser_page = browser.new_page()
        yield browser_page
        browser.close()


def test_homepage_language_and_theme(page):
    from playwright.sync_api import expect

    base_url = os.environ.get('FRONTEND_TEST_URL', 'http://localhost:8080')
    page.goto(f'{base_url}/?lang=EN')
    expect(page.locator('.hero-pitch')).to_contain_text('Automating the mundane')
    page.locator('.language-switch').get_by_role('button', name='FR').click()
    expect(page).to_have_url(re.compile(r'lang=FR'))
    expect(page.locator('.hero-eyebrow')).to_contain_text('AUTOMATISATION')
    page.locator('.theme-toggle').click()
    expect(page.locator('body')).to_have_class(re.compile(r'body--dark'))


def test_solution_route_does_not_misrepresent_future_demo(page):
    from playwright.sync_api import expect

    base_url = os.environ.get('FRONTEND_TEST_URL', 'http://localhost:8080')
    page.goto(f'{base_url}/flowdesk?lang=EN')
    expect(page.locator('.solution-coming')).to_have_text('Coming soon')
    expect(page.locator('.solution-section-heading').first).to_be_visible()
    page.locator('.solution-back').click()
    expect(page).to_have_url(re.compile(r'/\?lang=EN#business-solutions'))
