from app.gappers import db_init
from app.gappers.db_init import initialize_gap_database
from app.gappers.storage import save_gap_event


def save(symbol="NVDA"):
    return save_gap_event(
        symbol=symbol,
        trade_date="2026-08-17",
        detected_at="2026-08-17T13:00:00+00:00",
        gap_pct=3.0,
        gap_direction="up",
        previous_close=100.0,
        open_price=None,
        last_price=103.0,
        volume=100000,
        is_shortable=True,
        hard_to_borrow=False,
        source="test",
    )


def test_reports_new_then_duplicate(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        db_init,
        "DB_PATH",
        tmp_path / "gap_test.db",
    )

    initialize_gap_database()

    first = save()
    second = save()

    assert first["_created"] is True
    assert second["_created"] is False
    assert first["id"] == second["id"]
