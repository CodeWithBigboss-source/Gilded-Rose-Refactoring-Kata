# -*- coding: utf-8 -*-
"""
Characterization tests for the Gilded Rose inventory system.

These tests capture the EXISTING behavior of GildedRose.update_quality()
before any refactoring. They exist as a safety net: if a refactor changes
any of these results, a test will fail immediately.
"""
import pytest

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


if __name__ == '__main__':
    pytest.main()