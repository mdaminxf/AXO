import pyautogui

class RemoteControl:
    def __init__(self):
        pyautogui.FAILSAFE = True # Move mouse to corner to abort

    def handle_command(self, cmd_data):
        """
        Expects a dict with 'type', 'x', 'y', 'button', 'key', etc.
        """
        try:
            cmd_type = cmd_data.get("type")
            if cmd_type == "mouse_move":
                pyautogui.moveTo(cmd_data["x"], cmd_data["y"])
            elif cmd_type == "mouse_click":
                pyautogui.click(x=cmd_data.get("x"), y=cmd_data.get("y"), button=cmd_data.get("button", "left"))
            elif cmd_type == "key_press":
                pyautogui.press(cmd_data["key"])
            elif cmd_type == "text_type":
                pyautogui.write(cmd_data["text"])
        except Exception as e:
            print(f"Remote Control Error: {e}")
