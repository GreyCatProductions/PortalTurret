import queue
import threading

from MotorWorker import push_latest


class InputWorker(threading.Thread):
    def __init__(self, tilt_cmd_q: queue.Queue, pan_cmd_q: queue.Queue, stop_evt: threading.Event, mode_ref: dict):
        super().__init__(daemon=True)
        self.tilt_cmd_q = tilt_cmd_q
        self.pan_cmd_q = pan_cmd_q
        self.stop_evt = stop_evt
        self.mode_ref = mode_ref 

    def run(self):
        print(
            "\nCommands: l/r, stop, auto, manual, q\n"
            "Tip: type 'help' anytime.\n"
        )
        while not self.stop_evt.is_set():
            try:
                s = input("> ").strip().lower()
            except EOFError:
                self.stop_evt.set()
                return

            if not s:
                continue
            
            if s in ("q", "quit", "exit"):
                self.stop_evt.set()
                return

            if s in ("help", "?"):
                print("Commands: l/r (or left/right), stop, auto, manual, q")
                continue

            if s in ("auto",):
                self.mode_ref["mode"] = "auto"
                print("Mode = auto (face tracking)")
                continue

            if s in ("manual",):
                self.mode_ref["mode"] = "manual"
                push_latest(self.pan_cmd_q, ("stop",))
                push_latest(self.tilt_cmd_q, ("stop",))
                print("Mode = manual (keyboard)")
                continue

            if self.mode_ref["mode"] != "manual":
                print("Mode is not manual! Cant change directions manually before changing!")
                continue


            parts = s.split()
            cmd = parts[0].lower()

            RUN = "run"

            if cmd in ("l", "left"):
                push_latest(self.pan_cmd_q, (RUN, -1))
            elif cmd in ("r", "right"):
                push_latest(self.pan_cmd_q, (RUN, 1))
            elif cmd in ("u", "up"):
                push_latest(self.tilt_cmd_q, (RUN, 1))
            elif cmd in ("d", "down"):
                push_latest(self.tilt_cmd_q, (RUN, -1))
            elif cmd in ("stop"):
                push_latest(self.pan_cmd_q, ("stop",))
                push_latest(self.tilt_cmd_q, ("stop",))
            else:
                print("Unknown command. Type 'help'.")

