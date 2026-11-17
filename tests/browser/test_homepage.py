import re

import pytest

pytestmark = pytest.mark.browser


def test_production_launcher_serves_partfinder_without_catalog(page, deployed_homepage_url):
    from playwright.sync_api import expect

    page.goto(deployed_homepage_url, wait_until='networkidle')
    page.get_by_role('group', name=re.compile('^PartFinder:')).click()
    expect(page).to_have_url(re.compile(r'/partfinder\?lang=EN'))
    expect(page.get_by_role('heading', name='Find mechanical parts from an image or a description.')).to_be_visible()
    expect(page.get_by_text('Search unavailable', exact=True)).to_be_visible()
    expect(page.get_by_role('button', name='Search', exact=True)).to_be_disabled()


def test_language_switch_and_reload_preserve_both_theme_choices(page, homepage_url):
    from playwright.sync_api import expect

    dark = re.compile(r'\bbody--dark\b')
    page.goto(homepage_url, wait_until='networkidle')
    expect(page.locator('body')).not_to_have_class(dark)
    page.locator('.theme-toggle').click()
    page.wait_for_function("document.cookie.includes('portfolio_theme=dark')")
    page.get_by_role('button', name='FR', exact=True).click()
    expect(page.locator('body')).to_have_class(dark)
    expect(page.locator('.theme-toggle')).to_have_attribute('aria-label', 'Activer le mode clair')
    page.reload(wait_until='networkidle')
    expect(page.locator('body')).to_have_class(dark)
    page.locator('.theme-toggle').click()
    page.wait_for_function("document.cookie.includes('portfolio_theme=light')")
    page.get_by_role('button', name='EN', exact=True).click()
    expect(page.locator('body')).not_to_have_class(dark)
    page.reload(wait_until='networkidle')
    expect(page.locator('body')).not_to_have_class(dark)


def test_home_navigation_selects_its_showcase_row(page, homepage_url):
    from playwright.sync_api import expect

    page.goto(homepage_url, wait_until='networkidle')
    page.get_by_role('button', name='Business Solutions', exact=True).click()
    expect(page.locator('.main-content')).to_have_attribute('data-active-row', 'business')
    expect(page.locator('.research-section .showcase-collapse')).to_have_css('opacity', '0')
    business_cards = page.locator('.explore-section .showcase-card')
    expect(business_cards).to_have_count(3)
    assert business_cards.evaluate_all('cards => cards.every(card => card.classList.contains("is-row-active"))')

    page.get_by_role('button', name='Academic Projects', exact=True).click()
    expect(page.locator('.main-content')).to_have_attribute('data-active-row', 'academic')
    expect(page.locator('.explore-section .showcase-collapse')).to_have_css('opacity', '0')
    expect(page.locator('.projects-section .showcase-card').first).to_have_class(re.compile(r'\bis-row-active\b'))

    page.get_by_role('button', name='Research Papers', exact=True).click()
    expect(page.locator('.main-content')).to_have_attribute('data-active-row', 'research')
    expect(page.locator('.projects-section .showcase-collapse')).to_have_css('opacity', '0')


def test_clicking_partfinder_card_opens_demo(page, homepage_url):
    from playwright.sync_api import expect

    page.goto(homepage_url, wait_until='networkidle')
    page.get_by_role('group', name=re.compile('^PartFinder:')).click()
    expect(page).to_have_url(re.compile(r'/partfinder\?lang=EN'))
    expect(page.get_by_role('heading', name='Find mechanical parts from an image or a description.')).to_be_visible()


def test_inline_demo_reveal_preserves_arrow_and_restores_academic_cards(page, homepage_url):
    from playwright.sync_api import expect

    page.goto(homepage_url, wait_until='networkidle')
    card = page.get_by_role('group', name=re.compile('^PartFinder:'))
    image = card.locator('img')
    before = image.bounding_box()
    card.hover()
    expect(card).to_have_class(re.compile(r'\bis-hover-active\b'))
    expect(page.locator('.main-content')).to_have_attribute('data-active-row', 'business')
    expect(page.locator('.research-section .showcase-collapse')).to_have_css('grid-template-rows', '0px')
    after = image.bounding_box()
    assert abs(after['width'] - before['width']) < 1
    assert abs(after['height'] - before['height']) < 1
    card.locator('.demo-arrow').click()
    expect(page).to_have_url(re.compile(r'/partfinder\?lang=EN'))
    expect(page.get_by_role('heading', name='Find mechanical parts from an image or a description.')).to_be_visible()


def test_touch_reveal_and_arrow_do_not_conflict(browser, homepage_url):
    from playwright.sync_api import expect

    context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    try:
        page = context.new_page()
        page.goto(homepage_url, wait_until='networkidle')
        card = page.get_by_role('group', name=re.compile('^PartFinder:'))
        card.locator('.demo-arrow').tap()
        expect(page).to_have_url(re.compile(r'/partfinder\?lang=EN'))
        expect(page.get_by_role('heading', name='Find mechanical parts from an image or a description.')).to_be_visible()
    finally:
        context.close()
