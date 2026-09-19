# -*- coding: utf-8 -*-
"""
Characterization tests for the Gilded Rose inventory system.

These tests capture the EXISTING behavior of GildedRose.update_quality()
before any refactoring. They exist as a safety net: if a refactor changes
any of these results, a test will fail immediately.
"""
import pytest
import os

from gilded_rose import Item, GildedRose


def update_quality_once(name, sell_in, quality):
    """
    Helper: build a single item, run one day of update_quality(),
    and return the resulting (sell_in, quality) as a tuple.

    Keeping this in one place means every test below is a clean
    one-liner instead of repeating four lines of setup each time.
    """
    items = [Item(name, sell_in, quality)]
    gilded_rose = GildedRose(items)
    gilded_rose.update_quality()
    return items[0].sell_in, items[0].quality


class TestNormalItem:
    """
    A 'normal' item is anything that isn't Aged Brie, Sulfuras, or
    Backstage passes. It degrades in quality by 1 per day while in
    date, and by 2 per day once its sell_in has gone negative.
    Quality never drops below 0.
    """

    @pytest.mark.parametrize("sell_in, quality, expected_sell_in, expected_quality", [
        # (start_sell_in, start_quality, end_sell_in, end_quality)
        (10, 20, 9, 19),   # ordinary in-date day: -1 sell_in, -1 quality
        (5, 7, 4, 6),      # another ordinary day, different numbers
        (0, 5, -1, 3),     # crosses the sell-by date THIS call -> degrades by 2
        (-5, 10, -6, 8),   # already expired -> still degrades by 2
        (5, 0, 4, 0),      # quality floor: never goes negative
        (0, 1, -1, 0),     # floor still holds even mid-expiry-jump
    ])
    def test_degrades_correctly(self, sell_in, quality, expected_sell_in, expected_quality):
        actual_sell_in, actual_quality = update_quality_once("foo", sell_in, quality)
        assert actual_sell_in == expected_sell_in
        assert actual_quality == expected_quality

    def test_name_is_never_changed(self):
        items = [Item("+5 Dexterity Vest", 10, 20)]
        gilded_rose = GildedRose(items)
        gilded_rose.update_quality()
        assert items[0].name == "+5 Dexterity Vest"

class TestAgedBrie:
    """
    Aged Brie increases in quality as it ages — the opposite of
    normal items. It still caps at 50, and still 'degrades' (here,
    increases) twice as fast once expired.
    """

    @pytest.mark.parametrize("sell_in, quality, expected_sell_in, expected_quality", [
        (10, 20, 9, 21),    # ordinary in-date day: +1 quality
        (2, 0, 1, 1),       # starting from zero
        (0, 2, -1, 4),      # crosses sell-by THIS call -> +2, not +1
        (-3, 8, -4, 10),    # already expired -> still +2/day
        (5, 49, 4, 50),     # cap: 49 -> 50, stops there
        (0, 49, -1, 50),    # cap holds even during the double-jump
        (5, 50, 4, 50),     # already at cap -> stays at cap
    ])
    def test_increases_correctly(self, sell_in, quality, expected_sell_in, expected_quality):
        actual_sell_in, actual_quality = update_quality_once("Aged Brie", sell_in, quality)
        assert actual_sell_in == expected_sell_in
        assert actual_quality == expected_quality


class TestSulfuras:
    """
    Sulfuras is a legendary item: it is never sold and never decreases
    in quality. sell_in and quality both stay completely frozen,
    whether in date or expired. Its quality of 80 is the one
    legal exception to the normal 0-50 range.
    """

    @pytest.mark.parametrize("sell_in, quality", [
        (5, 80),    # in date
        (0, 80),    # exactly at sell-by
        (-5, 80),   # expired
    ])
    def test_never_changes(self, sell_in, quality):
        actual_sell_in, actual_quality = update_quality_once(
            "Sulfuras, Hand of Ragnaros", sell_in, quality
        )
        assert actual_sell_in == sell_in       # unchanged
        assert actual_quality == quality       # unchanged


class TestBackstagePasses:
    """
    Backstage passes increase in quality as the concert approaches:
      +1 when there are more than 10 days left
      +2 when there are 10 days or less
      +3 when there are 5 days or less
      drop to 0 the moment the concert has happened (sell_in < 0)
    Quality still caps at 50 on the way up.
    """

    NAME = "Backstage passes to a TAFKAL80ETC concert"

    @pytest.mark.parametrize("sell_in, quality, expected_sell_in, expected_quality", [
        (15, 20, 14, 21),   # >10 days left -> +1
        (11, 20, 10, 21),   # boundary: 11 days left is still the +1 tier
        (10, 20, 9, 22),    # boundary: 10 days left -> +2 tier starts
        (6, 20, 5, 22),     # still +2 tier
        (5, 20, 4, 23),     # boundary: 5 days left -> +3 tier starts
        (1, 20, 0, 23),     # still +3 tier
        (0, 20, -1, 0),     # concert just happened -> drops to 0
        (-1, 0, -2, 0),     # already past concert -> stays 0
        (10, 49, 9, 50),    # cap: 49 -> 50, stops (would've been 51)
        (5, 48, 4, 50),     # cap during the +3 tier
    ])
    def test_rises_then_drops_correctly(self, sell_in, quality, expected_sell_in, expected_quality):
        actual_sell_in, actual_quality = update_quality_once(self.NAME, sell_in, quality)
        assert actual_sell_in == expected_sell_in
        assert actual_quality == expected_quality

class TestGoldenMaster:
    """
    Regression safety net for the refactor. golden_master.txt was
    captured by running generate_golden_master.py against the
    ORIGINAL, unrefactored GildedRose implementation. This test
    reruns the exact same simulation against whatever code is
    currently in gilded_rose.py and asserts the output is byte-for-
    byte identical -- proving the refactor changed no behavior.
    """

    DAYS = 30

    def _build_items(self):
        return [
            Item("+5 Dexterity Vest", 10, 20),
            Item("Aged Brie", 2, 0),
            Item("Elixir of the Mongoose", 5, 7),
            Item("Sulfuras, Hand of Ragnaros", 0, 80),
            Item("Sulfuras, Hand of Ragnaros", -1, 80),
            Item("Backstage passes to a TAFKAL80ETC concert", 15, 20),
            Item("Backstage passes to a TAFKAL80ETC concert", 10, 49),
            Item("Backstage passes to a TAFKAL80ETC concert", 5, 49),
            Item("Conjured Mana Cake", 3, 6),
        ]

    def test_output_matches_golden_master(self):
        items = self._build_items()
        gilded_rose = GildedRose(items)
        lines = []
        for day in range(self.DAYS):
            lines.append(f"-------- day {day} --------")
            for item in items:
                lines.append(repr(item))
            gilded_rose.update_quality()
        actual_output = "\n".join(lines)

        golden_master_path = os.path.join(
            os.path.dirname(__file__), "golden_master.txt"
        )
        with open(golden_master_path) as f:
            expected_output = f.read()

        assert actual_output == expected_output

if __name__ == '__main__':
    pytest.main()