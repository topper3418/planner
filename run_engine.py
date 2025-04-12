from src import engine

import time

# cycle the engine once per second
if __name__ == "__main__":
   try:
      while True:
          engine.cycle()
          time.sleep(1)
   except KeyboardInterrupt:
      print("Stopping the engine.")
