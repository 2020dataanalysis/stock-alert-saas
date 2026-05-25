import argparse

from app.market_state.replay_service import replay_quotes


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--symbol",
        required=True
    )

    parser.add_argument(
        "--date",
        required=True
    )

    args = parser.parse_args()

    results = replay_quotes(
        symbol=args.symbol,
        date=args.date,
        persist_events=True
    )

    for result in results:

        features = result["features"]

        print(
            f"{result['timestamp']} "
            f"{result['symbol']} "
            f"last={result['price']:.2f} "
            f"v5={features['velocity_5s_pct']:.3f}% "
            f"v10={features['velocity_10s_pct']:.3f}% "
            f"r30={features['range_30s_pct']:.3f}% "
            f"shock={features['shock_score']:.1f} "
            f"trend={features['trend_score']:.1f} "
            f"noise={features['noise_score']:.1f} "
            f"state={result['state']} "
            f"permission={result['trade_permission']}"
        )


if __name__ == "__main__":
    main()
