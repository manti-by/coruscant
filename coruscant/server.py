import RPi.GPIO as GPIO
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.settings import PUMP_MAP


app = FastAPI()


class RelayState(BaseModel):
    relay_id: str
    state: str


@app.post("/relay/")
async def set_relay(request: RelayState) -> dict:
    setup_gpio()

    for pin, rid in PUMP_MAP.items():
        if rid == request.relay_id:
            target_state = GPIO.HIGH if request.state.upper() == "ON" else GPIO.LOW
            if set_gpio_state(gpio_pin=pin, target_state=target_state):
                return {"success": True}
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
