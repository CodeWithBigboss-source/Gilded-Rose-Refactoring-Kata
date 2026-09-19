# -*- coding: utf-8 -*-
"""
One-off script: runs GildedRose for many days across every item
category and prints the state after each day. Run this ONCE against
the ORIGINAL unmodified code to capture golden_master.txt. After
that, this script is not run again as part of testing -- the saved
file is the permanent reference.
"""
from gilded_rose import Item, GildedRose

DAYS = 30


def build_items():
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


if __name__ == "__main__":
    items = build_items()
    gilded_rose = GildedRose(items)
    lines = []
    for day in range(DAYS):
        lines.append(f"-------- day {day} --------")
        for item in items:
            lines.append(repr(item))
        gilded_rose.update_quality()
    output = "\n".join(lines)
    print(output)
    with open("golden_master.txt", "w") as f:
        f.write(output)