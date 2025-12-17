import RPi.GPIO as GPIO


def setup_gpio() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)


def set_gpio_state(gpio_pin: int, target_state: bool) -> bool:
    GPIO.setup(gpio_pin, GPIO.OUT)
    current_state = GPIO.input(gpio_pin)
    if current_state != target_state:
        GPIO.output(gpio_pin, GPIO.LOW if target_state else GPIO.HIGH)
        return True
    return False


def close_gpio() -> None:
    GPIO.cleanup()
