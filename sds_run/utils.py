from datetime import datetime
import threading
import time
import sys
import itertools
from contextlib import contextmanager

def convert_date_to_simulation_time(start_date_str: str, days_to_simulate: int):
    """
    Converts a start date and duration into simulation-ready time units.

    Args:
        start_date_str (str): The start date in 'YYYY-MM-DD' format.
        days_to_simulate (int): The number of days to simulate.

    Returns:
        tuple[int, int]: A tuple containing:
                         - The start hour of the year (0-8759).
                         - The total number of simulation points (at 15-min resolution).
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Error: start_date must be in YYYY-MM-DD format.")

    year = start_date.year
    start_of_year = datetime(year, 1, 1)
    
    time_delta = start_date - start_of_year
    start_hour = int(time_delta.total_seconds() / 3600)
    
    points_per_day = 96  # 24 hours * 4 points/hour (15-min steps)
    number_of_points = days_to_simulate * points_per_day

    return start_hour, number_of_points

#(full vibe coding)
class Spinner:
    """A simple, thread-safe terminal spinner."""
    def __init__(self, message: str = "Loading...", delay: float = 0.7):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        while self.running:
            char = next(self.spinner)
            sys.stdout.write(f'\r{self.message} {char}')
            sys.stdout.flush()
            time.sleep(self.delay)

    def start(self):
        """Starts the spinner in a separate thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self):
        """Stops the spinner and cleans up the line."""
        if not self.running:
            return
        self.running = False
        self.thread.join()
        # Limpa a linha escrevendo espaços em branco sobre ela
        sys.stdout.write(f'\r{" " * (len(self.message) + 2)}\r')
        sys.stdout.flush()