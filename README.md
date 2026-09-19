# Gilded Rose Refactoring Kata

Solution to the TechieMinions Gilded Rose code challenge: refactor a
legacy inventory system, add unit tests, fix bugs, and add support for
a new "Conjured" item category — without modifying the `Item` class.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate      # Git Bash on Windows
pip install pytest
```

## Running the tests

```bash
python -m pytest -v
```

34 tests, all passing. Includes a golden-master regression test
(`TestGoldenMaster`) that compares a 30-day simulation's full output
against a saved reference file, to prove the refactor did not change
any existing behavior.

## Manual demo

```bash
python texttest_fixture.py 30
```

Prints day-by-day state for a sample set of items, for eyeballing.

## Approach

1. **Characterization tests first.** Before touching any production
   code, tests were written against the *original* implementation to
   lock in its exact existing behavior — including two non-obvious
   quirks (see `ASSUMPTIONS.md`, items 1 and 2).
2. **Golden-master test.** A full multi-day simulation across every
   item type was captured as a reference file, so any accidental
   behavior change during refactoring would be caught immediately.
3. **Refactor.** `GildedRose.update_quality()`'s deeply nested
   conditionals were replaced with a strategy pattern: one small
   updater class per item category (`item_updaters.py`), selected by
   a factory function. The full test suite, including the golden
   master, was run after every change.
4. **Conjured items, via TDD.** Failing tests were written first
   (see commit history), then `ConjuredUpdater` was added to make
   them pass — mirroring `NormalItemUpdater`'s shape at twice the
   degradation rate.
5. **Boundary and edge-case coverage.** Tests cover quality
   floors/ceilings, sell-by boundaries for backstage passes, and
   Sulfuras's exemption from all normal rules.

See `ASSUMPTIONS.md` for every place the brief was ambiguous and how
it was resolved.

## Design decision: strategy pattern over subclassing `Item`

Subclassing `Item` per category was considered and rejected — the
system doesn't control how `Item` instances are constructed, so a
subclass-based design has no way to select the right subclass at
creation time. A small updater class per category, selected by a
factory function that reads `item.name`, avoids that problem entirely
and keeps `Item` completely untouched. Adding a new item category is
one new class plus one line in the factory.

## What was left unchanged

Per the assignment's constraint, `Item` (in `gilded_rose.py`) was not
modified in any way — no new fields, methods, or behavior.