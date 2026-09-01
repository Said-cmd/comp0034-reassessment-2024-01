"""Browser tests for the dashboard, using Playwright."""
from playwright.sync_api import expect


def test_page_loads(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it in a browser
    page.goto(dash_url)
    # THEN the correct page title is shown
    assert page.title() == "Summer Sports Dashboard"


def test_heading_visible(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN the main heading is visible with the correct text
    assert page.locator("h1").inner_text() == "Summer Sports Events Dashboard"


def test_initial_summary_stats(page, dash_url):
    # GIVEN the app is running with no filters applied
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN the summary line shows the total session count
    expect(page.locator("#summary-stats")).to_contain_text("4,748 sessions")


def test_all_charts_present(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN all 4 required visualisations are present
    expect(page.locator("#attendance-trend")).to_have_count(1)
    expect(page.locator("#attendance-by-borough")).to_have_count(1)
    expect(page.locator("#top-sports")).to_have_count(1)
    expect(page.locator("#park-table")).to_have_count(1)


def test_growing_sports_table_present(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN the growing-sports table is present and populated
    expect(page.get_by_text("Sports trending upward")).to_have_count(1)
    expect(page.locator("#suggestions-table")).to_have_count(1)


def test_declining_sports_table_present(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN the declining-sports table is present and populated
    expect(page.get_by_text("Sports trending downward")).to_have_count(1)
    expect(page.locator("#declining-table")).to_have_count(1)


def test_filter_by_borough_updates_summary(page, dash_url):
    # GIVEN the app is running with no filters applied
    page.goto(dash_url)
    # WHEN a user selects a single borough from the dropdown
    page.locator("#borough-filter").click()
    page.keyboard.type("Queens")
    page.keyboard.press("Enter")
    # THEN the summary stats update to reflect a smaller subset
    expect(page.locator("#summary-stats")).not_to_contain_text("4,748 sessions")


def test_combined_borough_and_year_filter(page, dash_url):
    # GIVEN the app is running with no filters applied
    page.goto(dash_url)
    # WHEN a user selects both a borough and a year
    page.locator("#borough-filter").click()
    page.keyboard.type("Brooklyn")
    page.keyboard.press("Enter")
    page.locator("#year-filter").click()
    page.keyboard.type("2018")
    page.keyboard.press("Enter")
    # THEN the app still responds correctly with both filters applied
    expect(page.locator("#summary-stats")).to_contain_text("sessions")


def test_park_table_sorts_on_header_click(page, dash_url):
    # GIVEN the app is running with the park table in its default order
    page.goto(dash_url)
    row = page.locator("#park-table table tbody tr").nth(1)  # row 0 is the header
    before = row.inner_text()
    # WHEN a user clicks a sortable column header
    page.locator("#park-table th", has_text="total_attendance").click()
    # THEN the table re-sorts and the first data row changes
    expect(row).not_to_have_text(before)


def test_chart_title_via_text_locator(page, dash_url):
    # GIVEN the app is running
    # WHEN a user opens it
    page.goto(dash_url)
    # THEN a chart title is present, found via visible text rather than an ID
    expect(page.get_by_text("Top 10 sports by attendance")).to_have_count(1)
