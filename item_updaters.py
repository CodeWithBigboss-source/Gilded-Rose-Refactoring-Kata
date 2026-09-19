# -*- coding: utf-8 -*-
"""
Updater classes for each item category in the Gilded Rose system.

Each updater knows how to age exactly one category of item by one
day. GildedRose.update_quality() will simply ask a factory function
"which updater handles this item?" and delegate to it -- replacing
the original deeply nested conditional logic.

The Item class itself (in gilded_rose.py) is never modified here,
per the assignment's constraint.
"""

MAX_QUALITY = 50
MIN_QUALITY = 0


class NormalItemUpdater:
    """
    Handles any item that isn't Aged Brie, Sulfuras, or Backstage
    passes: quality drops by 1 per day while in date, and by 2 per
    day once sell_in has gone negative. Quality never drops below 0.
    """

    def update(self, item):
        item.sell_in -= 1
        self._degrade(item, amount=1)
        if item.sell_in < 0:
            self._degrade(item, amount=1)

    def _degrade(self, item, amount):
        item.quality = max(MIN_QUALITY, item.quality - amount)


class AgedBrieUpdater:
    """
    Aged Brie increases in quality as it ages -- the opposite of a
    normal item. It still caps at 50, and still changes twice as
    fast once expired (here, that means +2 instead of +1).
    """

    def update(self, item):
        item.sell_in -= 1
        self._improve(item, amount=1)
        if item.sell_in < 0:
            self._improve(item, amount=1)

    def _improve(self, item, amount):
        item.quality = min(MAX_QUALITY, item.quality + amount)


class SulfurasUpdater:
    """
    Sulfuras is legendary: sell_in and quality never change, in date
    or expired. Its quality of 80 is the one legal exception to the
    normal 0-50 range, and this updater must never clamp it.
    """

    def update(self, item):
        pass  # frozen -- nothing to do, by design


class BackstagePassUpdater:
    """
    Backstage passes rise in value as the concert approaches, then
    become worthless once the concert has happened:
      sell_in > 10  -> +1
      6 <= sell_in <= 10 -> +2
      1 <= sell_in <= 5  -> +3
      sell_in < 0 (concert over) -> quality becomes 0
    Quality still caps at 50 on the way up.
    """

    def update(self, item):
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = 0
        elif item.sell_in < 5:
            self._improve(item, amount=3)
        elif item.sell_in < 10:
            self._improve(item, amount=2)
        else:
            self._improve(item, amount=1)

    def _improve(self, item, amount):
        item.quality = min(MAX_QUALITY, item.quality + amount)


AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"

_normal_updater = NormalItemUpdater()
_aged_brie_updater = AgedBrieUpdater()
_sulfuras_updater = SulfurasUpdater()
_backstage_updater = BackstagePassUpdater()


def get_updater_for(item):
    """
    Given an item, return the updater instance responsible for
    aging it by one day. This is the single place that maps item
    names to behavior -- add a new category here, not by adding
    more branches inside GildedRose.
    """
    if item.name == AGED_BRIE:
        return _aged_brie_updater
    if item.name == SULFURAS:
        return _sulfuras_updater
    if item.name == BACKSTAGE_PASSES:
        return _backstage_updater
    return _normal_updater


if __name__ == "__main__":
    print("item_updaters.py loaded successfully — no syntax errors.")