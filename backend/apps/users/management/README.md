# Management commands

## Demo data seeder

Dev-only Django command for generating realistic demo data for analytics/stats testing. Requires `DEBUG=True`.

```bash
python manage.py seed_demo_data                  # create demo data
python manage.py seed_demo_data --flush          # delete and recreate demo accounts
python manage.py seed_demo_data --days 120       # use 120 days of history
python manage.py seed_demo_data --seed 42        # use a reproducible random seed
```

**Demo accounts** — password: `Demo12345!`

* `demo_fitness`
* `demo_focus`
* `demo_wellness`
* `demo_habits`

Each account gets 6 signals, 2 boards, and up to 300 days of events with randomized values, trends, weekday patterns, shared events, and occasional notes.

Re-running without `--flush` fails if demo accounts already exist.
