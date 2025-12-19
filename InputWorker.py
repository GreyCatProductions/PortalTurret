import queue
import threading

from MotorWorker import push_latest


class InputWorker(threading.Thread):
    def __init__(self, cmd_q: queue.Queue, stop_evt: threading.Event, mode_ref: dict):
        super().__init__(daemon=True)
        self.cmd_q = cmd_q
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

            if s in ("q", "quit", "exit", "stop"):
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
                push_latest(self.cmd_q, ("STOP"))
                print("Mode = manual (keyboard)")
                continue

            parts = s.split()
            cmd = parts[0]

            if cmd in ("l", "left"):
                push_latest(self.cmd_q, ("run", -1))
            elif cmd in ("r", "right"):
                push_latest(self.cmd_q, ("run", 1))
            elif cmd == "stop":
                push_latest(self.cmd_q, ("stop",))
            else:
                print("Unknown command. Type 'help'.")

