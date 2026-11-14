from io import BytesIO

from PIL import Image
import pytest

pytestmark = pytest.mark.browser


def test_text_search_details_and_reset_use_real_catalog_and_query_lifecycle(page, partfinder_url):
    from playwright.sync_api import expect

    page.goto(partfinder_url, wait_until='networkidle')
    expect(page.get_by_text('Ready to search', exact=True)).to_be_visible()
    page.get_by_label('Text description', exact=True).fill('a toothed gear')
    page.get_by_role('button', name='Search', exact=True).click()
    expect(page.get_by_role('heading', name='Search results', exact=True)).to_be_visible()
    expect(page.get_by_text('Test gear', exact=True)).to_be_visible()
    page.get_by_role('button', name='Details', exact=True).first.click()
    expect(page.get_by_role('button', name='Close details', exact=True)).to_be_visible()
    page.get_by_role('button', name='Close details', exact=True).click()
    page.get_by_role('button', name='Reset', exact=True).click()
    expect(page.get_by_role('heading', name='Search results', exact=True)).to_have_count(0)
    expect(page.get_by_label('Text description', exact=True)).to_have_value('')


def test_image_upload_crosses_real_nicegui_http_boundary_and_can_be_searched(page, partfinder_url):
    from playwright.sync_api import expect

    data = BytesIO()
    Image.new('RGB', (32, 24), 'gray').save(data, format='PNG')
    page.goto(partfinder_url, wait_until='networkidle')
    expect(page.get_by_text('Ready to search', exact=True)).to_be_visible()
    with page.expect_response(lambda response: '/upload/' in response.url and response.request.method == 'POST') as upload:
        page.locator('input[type=file]').set_input_files({'name': 'part.png', 'mimeType': 'image/png', 'buffer': data.getvalue()})
    assert upload.value.status == 200
    expect(page.get_by_text('Image ready. Search with the image alone or add a description.', exact=True)).to_be_visible()
    page.get_by_role('button', name='Search', exact=True).click()
    expect(page.get_by_text('Test gear', exact=True)).to_be_visible()
