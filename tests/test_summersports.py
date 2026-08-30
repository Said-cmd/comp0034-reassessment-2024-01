"""Browser tests for the Summer Sports dashboard."""
from playwright.sync_api import expect

def test_page_loads(page, dash_url):
    page.goto(dash_url)
    assert page.title() == "Summer Sports Dashboard"

def test_heading_visible(page, dash_url):
    page.goto(dash_url)
    assert page.locator("h1").inner_text() == "Summer Sports Events Dashboard"

def test_initial_summary_stats(page, dash_url):
    page.goto(dash_url)
    expect(page.locator("#summary-stats")).to_contain_text("4,748 sessions")

def test_all_charts_present(page, dash_url):
    page.goto(dash_url)
    assert page.locator("#attendance-trend").count() == 1
    assert page.locator("#attendance-by-borough").count() == 1
    assert page.locator("#top-sports").count() == 1
    assert page.locator("#park-table").count() == 1

def test_filter_by_borough_updates_summary(page, dash_url):
    page.goto(dash_url)
    page.locator("#borough-filter").click()
    page.keyboard.type("Queens")
    page.keyboard.press("Enter")
    expect(page.locator("#summary-stats")).not_to_contain_text("4,748 sessions")

def test_combined_borough_and_year_filter(page, dash_url):
    page.goto(dash_url)
    page.locator("#borough-filter").click()
    page.keyboard.type("Brooklyn")
    page.keyboard.press("Enter")
    page.locator("#year-filter").click()
    page.keyboard.type("2018")
    page.keyboard.press("Enter")
    expect(page.locator("#summary-stats")).to_contain_text("sessions")

def test_park_table_sorts_on_header_click(page, dash_url):
    page.goto(dash_url)
    row = page.locator("#park-table table tbody tr").nth(1)  # row 0 is the header
    before = row.inner_text()
    page.locator("#park-table th", has_text="total_attendance").click()
    expect(row).not_to_have_text(before)

def test_chart_title_via_text_locator(page, dash_url):
    page.goto(dash_url)
    expect(page.get_by_text("Top 10 sports by attendance")).to_have_count(1)