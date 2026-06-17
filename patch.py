from pathlib import Path

f = Path("simulator/mqtt_simulator.py")

text = f.read_text()

text = text.replace(
    "Path(__file__).parent / '../STOP_SIMULATOR'",
    "Path(__file__).resolve().parent / 'STOP_SIMULATOR'"
)

text = text.replace(
    'Path(__file__).parent / "../STOP_SIMULATOR"',
    "Path(__file__).resolve().parent / 'STOP_SIMULATOR'"
)

f.write_text(text)

print("✅ SENTINEL path fixed")
