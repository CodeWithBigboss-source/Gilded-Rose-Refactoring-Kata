# Assumptions

The brief for this challenge is intentionally informal in places. Per
the instructions ("if you have any confusion, please take an assumption
and state it clearly"), here are the assumptions made while building
this solution, and the reasoning behind each.

## 1. Update ordering matches the original code exactly
`sell_in` is decremented *before* checking whether the item has expired
in the same call. This means an item that crosses its sell-by date on
a given day immediately receives its "expired" quality change (e.g. a
normal item can drop by 2 on the very day it expires, not the day
after). This was existing behavior in the original code and is
preserved deliberately — it is not something the brief specifies in
prose, but changing it would be a behavior change, not a refactor.

## 2. Aged Brie's quality increase doubles after expiry
The brief never explicitly says Aged Brie's "reverse degradation" also
doubles once expired — it only states the degradation-doubling rule for
normal items. The original code does apply a doubled increase to Aged
Brie after its sell-by date, so this behavior is preserved for
consistency with the existing system.

## 3. "Conjured" items are matched by name prefix, not exact match
The supplier note describes a *category* of items ("a supplier of
conjured items"), and the sample item name in the provided test fixture
is "Conjured Mana Cake" — not the literal string "Conjured". The
Conjured updater is therefore selected for any item whose name starts
with "Conjured", so that future items like "Conjured Health Potion"
would be handled correctly without code changes.

## 4. Quality is clamped upward, never forced downward
The brief states quality "is never more than 50" — a ceiling on
increases, not a hard clamp on construction. Items are never forced
down to 50 if they start above it (aside from Sulfuras, which is
explicitly exempt at quality 80). In practice, no such item appears in
the provided test data, but this is the more literal reading of the
rule as written.

## 5. The `Item` class is treated as fully off-limits
The brief's "goblin" warning refers to the `Item` class (in some
language ports of this kata, `Item` is a constructor function rather
than a class, which is the likely source of the wording). No fields,
methods, or behavior were added to `Item`; all new logic lives in
`item_updaters.py` and operates on `Item` instances from the outside.

## 6. Backstage passes' tier boundaries
"10 days or less" and "5 days or less" are read as `sell_in <= 10` and
`sell_in <= 5` *after* the day's decrement, matching the original
code's `sell_in < 11` / `sell_in < 6` checks (which operate on the
already-decremented value). This was verified against the original
code's actual behavior via the characterization test suite before any
refactoring took place.