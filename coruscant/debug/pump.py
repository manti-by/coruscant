import argparse
import sys

import RPi.GPIO as GPIO

from coruscant.services.gpio import close_gpio, set_gpio_state, setup_gpio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set a GPIO pin state to on/off using BOARD numbering."
    )
    parser.add_argument(
        "state",
        choices=["on", "off"],
        help="Desired state for the GPIO pin.",
    )
    parser.add_argument(
        "pin",
        type=int,
        help="GPIO pin number (BOARD numbering).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    setup_gpio()
    try:
        target_state = GPIO.HIGH if args.state == "on" else GPIO.LOW
        changed = set_gpio_state(args.pin, target_state)

        msg = f"Pin {args.pin} set to {args.state}."
        if not changed:
            msg += " (already in requested state)"
        print(msg)
    except (ValueError, RuntimeError) as exc:  # pragma: no cover - simple CLI error path
        print(f"Error while setting pin {args.pin}: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        close_gpio()

