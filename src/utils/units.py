__all__ = ["celsius_to_fahrenheit"]


def celsius_to_fahrenheit(celsius: float) -> float:
    """Converts a temperature in celsius to fahrenheit."""
    return (celsius * (9 / 5)) + 32
