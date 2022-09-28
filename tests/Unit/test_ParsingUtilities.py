import src.ParsingUtilities
from lxml import etree
from datetime import datetime, timezone, timedelta

def test_get_date_from_node():
    root = etree.fromstring("<root><pubDate>Thu, 29 Sep 2022 13:02:03 -0400</pubDate></root>")
    assert(src.ParsingUtilities.get_date_from_node(root) == datetime(year=2022, month=9, day=29, hour=13, minute=2, second=3, tzinfo=timezone(timedelta(days=-1, seconds=72000))))


def test_GetLastItemInformation():    
    rss_contents = """
    <rss version="2.0">
        <channel>
            <title>
                <![CDATA[ Announcements & Events Latest Topics ]]>
            </title>
            <link>https://forums.warframe.com/forum/170-announcements-events/</link>
            <description>
                <![CDATA[ Announcements & Events Latest Topics ]]>
            </description>
            <language>fr</language>
            <item>
                <title>Cross Platform Play Initial Public Test</title>
                <link>https://forums.warframe.com/topic/1326149-cross-platform-play-initial-public-test/</link>
                <description>description contents</description>
                <guid isPermaLink="false">1326149</guid>
                <pubDate>Thu, 29 Sep 2022 13:02:03 -0400</pubDate>
            </item>
            <item>
                <title>
                    <![CDATA[ PSA: Recent 'Break Narmer' Reset Clarification & Upcoming Fix ]]>
                </title>
                <link>https://forums.warframe.com/topic/1326012-psa-recent-break-narmer-reset-clarification-upcoming-fix/</link>
                <description>
                    description
                </description>
                <guid isPermaLink="false">1326012</guid>
                <pubDate>Wed, 28 Sep 2022 18:19:31 -0400</pubDate>
            </item>
            <item>
                <title>Dog Days Returns on all Platforms!</title>
                <link>https://forums.warframe.com/topic/1313502-dog-days-returns-on-all-platforms/</link>
                <description>
                    description
                </description>
                <guid isPermaLink="false">1313502</guid>
                <pubDate>Thu, 09 Jun 2022 10:07:33 -0400</pubDate>
            </item>
        </channel>
    </rss>
    """

    model = src.ParsingUtilities.GetLastItemInformation(rss_contents)

    assert(model.title == "Cross Platform Play Initial Public Test")