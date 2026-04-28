import ast
import colorsys
import math
import operator
import tkinter as tk


class SafeCalculator:
    """Small safe evaluator for calculator expressions."""

    BINARY_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def __init__(self, angle_mode_getter):
        self.angle_mode_getter = angle_mode_getter

    def evaluate(self, expression):
        if not expression:
            return 0

        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported constant")

        if isinstance(node, ast.Name):
            if node.id in self.CONSTANTS:
                return self.CONSTANTS[node.id]
            raise ValueError("Unknown name")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.BINARY_OPERATORS:
                raise ValueError("Unsupported operator")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.BINARY_OPERATORS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.UNARY_OPERATORS:
                raise ValueError("Unsupported unary operator")
            return self.UNARY_OPERATORS[op_type](self._eval_node(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported function")
            if len(node.args) != 1 or node.keywords:
                raise ValueError("Wrong function arguments")

            function = self._functions().get(node.func.id)
            if function is None:
                raise ValueError("Unknown function")
            return function(self._eval_node(node.args[0]))

        raise ValueError("Unsupported expression")

    def _functions(self):
        return {
            "sin": self._angle_function(math.sin),
            "cos": self._angle_function(math.cos),
            "tan": self._angle_function(math.tan),
            "asin": self._inverse_angle_function(math.asin),
            "acos": self._inverse_angle_function(math.acos),
            "atan": self._inverse_angle_function(math.atan),
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "sqrt": math.sqrt,
            "ln": math.log,
            "log": math.log10,
            "exp": math.exp,
            "abs": abs,
            "factorial": self._factorial,
        }

    def _angle_function(self, function):
        def wrapper(value):
            if self.angle_mode_getter() == "DEG":
                value = math.radians(value)
            return function(value)

        return wrapper

    def _inverse_angle_function(self, function):
        def wrapper(value):
            result = function(value)
            if self.angle_mode_getter() == "DEG":
                result = math.degrees(result)
            return result

        return wrapper

    @staticmethod
    def _factorial(value):
        if value < 0 or int(value) != value:
            raise ValueError("Factorial is only defined for non-negative integers")
        return math.factorial(int(value))


class Calculator:
    NUMBER_CHARS = set("0123456789")
    VALUE_END_CHARS = set("0123456789.)")
    OPERATOR_CHARS = set("+-*/%")
    RAINBOW = [
        "#ff1744",
        "#ff9100",
        "#ffea00",
        "#00e676",
        "#00e5ff",
        "#2979ff",
        "#d500f9",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Инженерный калькулятор")
        self.root.geometry("560x660")
        self.root.minsize(500, 600)

        self.expression = ""
        self.input_text = tk.StringVar(value="0")
        self.angle_mode = tk.StringVar(value="DEG")
        self.evaluator = SafeCalculator(self.angle_mode.get)
        self.buttons = {}
        self.button_base_styles = {}
        self.rgb_phase = 0

        self.create_widgets()
        self.animate_display_rgb()
        self.root.bind_all("<Key>", self.on_key_press)

    def create_widgets(self):
        self.root.configure(bg="#050013")

        self.display_glow = tk.Frame(self.root, bg="#ff1744", bd=0)
        self.display_glow.pack(fill=tk.X, padx=12, pady=(12, 8))

        display_frame = tk.Frame(self.display_glow, bg="#08031f")
        display_frame.pack(fill=tk.X, padx=5, pady=5)

        self.mode_label = tk.Label(
            display_frame,
            textvariable=self.angle_mode,
            font=("Segoe UI Semibold", 11),
            bg="#08031f",
            fg="#00e5ff",
            anchor="w",
        )
        self.mode_label.pack(fill=tk.X, padx=10, pady=(8, 0))

        self.display = tk.Entry(
            display_frame,
            textvariable=self.input_text,
            font=("Segoe UI Semibold", 30),
            justify="right",
            readonlybackground="#08031f",
            bg="#08031f",
            fg="#ffffff",
            bd=0,
            relief=tk.FLAT,
            state="readonly",
            takefocus=0,
            insertbackground="#ffffff",
        )
        self.display.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=18)

        buttons_frame = tk.Frame(self.root, bg="#050013")
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

        buttons = [
            ["DEG/RAD", "sin", "cos", "tan", "C", "←"],
            ["asin", "acos", "atan", "π", "e", "±"],
            ["x²", "x³", "xʸ", "√", "1/x", "/"],
            ["10ˣ", "eˣ", "ln", "log", "mod", "*"],
            ["(", ")", "n!", "|x|", "%", "-"],
            ["7", "8", "9", "CE", ".", "+"],
            ["4", "5", "6", "sinh", "cosh", "tanh"],
            ["1", "2", "3", "0", "=", "="],
        ]

        for row_index, row in enumerate(buttons):
            buttons_frame.rowconfigure(row_index, weight=1, uniform="buttons")
            for column_index in range(6):
                buttons_frame.columnconfigure(column_index, weight=1, uniform="buttons")

            for column_index, button_text in enumerate(row):
                column_span = 2 if button_text == "=" and column_index == 4 else 1
                if button_text == "=" and column_index == 5:
                    continue
                self.create_button(
                    buttons_frame,
                    button_text,
                    row_index,
                    column_index,
                    column_span,
                )

    def create_button(self, parent, text, row, column, column_span=1):
        bg = "#15143d"
        fg = "#ffffff"

        if text in self.OPERATOR_CHARS or text in {"=", "mod", "xʸ"}:
            bg = "#ff7a00"
        elif text in {"C", "CE", "←"}:
            bg = "#ff1744"
        elif text in {"DEG/RAD"}:
            bg = "#00c2ff"
            fg = "#00111d"
        elif text in self.NUMBER_CHARS or text == ".":
            bg = "#19f5aa"
            fg = "#06120e"
        elif text not in self.NUMBER_CHARS and text != ".":
            bg = "#8f00ff"

        button = tk.Button(
            parent,
            text=text,
            font=("Segoe UI Semibold", 13),
            bg=bg,
            fg=fg,
            activebackground="#fff200",
            activeforeground="#ffffff",
            command=lambda: self.on_button_click(text),
            relief=tk.RAISED,
            bd=2,
            highlightthickness=2,
            highlightbackground="#ffffff",
            cursor="hand2",
        )
        button.grid(
            row=row,
            column=column,
            columnspan=column_span,
            sticky="nsew",
            padx=3,
            pady=3,
        )
        self.buttons.setdefault(text, []).append(button)
        self.button_base_styles[button] = {"bg": bg, "fg": fg, "activebackground": "#fff200"}

    def on_button_click(self, char):
        self.flash_button(char)

        if char in self.NUMBER_CHARS:
            self.append_value(char)
        elif char == ".":
            self.append_decimal_point()
        elif char in {"+", "-", "*", "/", "%"}:
            self.append_operator(char)
        elif char == "mod":
            self.append_operator("%")
        elif char == "=":
            self.calculate()
        elif char in {"C", "CE"}:
            self.clear()
        elif char == "←":
            self.backspace()
        elif char == "DEG/RAD":
            self.toggle_angle_mode()
        elif char == "±":
            self.toggle_sign()
        elif char == "π":
            self.append_value("pi")
        elif char == "e":
            self.append_value("e")
        elif char == "xʸ":
            self.append_operator("**")
        elif char == "x²":
            self.apply_to_current_operand(lambda operand: f"({operand})**2", "0**2")
        elif char == "x³":
            self.apply_to_current_operand(lambda operand: f"({operand})**3", "0**3")
        elif char == "√":
            self.append_function("sqrt")
        elif char == "1/x":
            self.apply_to_current_operand(lambda operand: f"1/({operand})", "1/(")
        elif char == "10ˣ":
            self.append_function("pow10")
        elif char == "eˣ":
            self.append_function("exp")
        elif char == "n!":
            self.apply_to_current_operand(lambda operand: f"factorial({operand})", "factorial(")
        elif char == "|x|":
            self.apply_to_current_operand(lambda operand: f"abs({operand})", "abs(")
        elif char in {"sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "ln", "log"}:
            self.append_function(char)
        elif char in {"(", ")"}:
            self.append_parenthesis(char)

    def on_key_press(self, event):
        char = event.char

        if char in self.NUMBER_CHARS:
            self.on_button_click(char)
            return "break"
        if char in {"+", "-", "*", "/", "%", ".", "(", ")"}:
            self.on_button_click(char)
            return "break"
        if char == "^":
            self.on_button_click("xʸ")
            return "break"
        if event.keysym in {"Return", "KP_Enter"}:
            self.on_button_click("=")
            return "break"
        if event.keysym == "BackSpace":
            self.on_button_click("←")
            return "break"
        if event.keysym == "Escape":
            self.on_button_click("C")
            return "break"

        return None

    def append_value(self, value):
        if self.input_text.get() == "Ошибка":
            self.clear()

        if value in self.NUMBER_CHARS:
            if self.expression == "0":
                self.expression = value
            else:
                if self.expression.endswith(("pi", "e")) or self.expression.endswith(")"):
                    self.expression += "*"
                self.expression += value
        else:
            if self.needs_implicit_multiplication():
                self.expression += "*"
            self.expression += value
        self.refresh_display()

    def append_decimal_point(self):
        if self.input_text.get() == "Ошибка":
            self.clear()

        current_number = self.current_number()
        if "." not in current_number:
            if not current_number:
                self.expression += "0"
            self.expression += "."
            self.refresh_display()

    def append_operator(self, operator_text):
        if self.input_text.get() == "Ошибка":
            self.clear()

        if not self.expression:
            if operator_text == "-":
                self.expression = "-"
            self.refresh_display()
            return

        if self.expression.endswith("**"):
            self.expression = self.expression[:-2] + operator_text
        elif self.expression[-1] in "+-*/%":
            self.expression = self.expression[:-1] + operator_text
        else:
            self.expression += operator_text
        self.refresh_display()

    def append_function(self, name):
        if name == "pow10":
            self.apply_to_current_operand(lambda operand: f"10**({operand})", "10**(")
        else:
            self.apply_to_current_operand(lambda operand: f"{name}({operand})", f"{name}(")

    def append_parenthesis(self, parenthesis):
        if parenthesis == "(" and self.needs_implicit_multiplication():
            self.expression += "*"
        self.expression += parenthesis
        self.refresh_display()

    def apply_to_current_operand(self, transform, fallback):
        if self.input_text.get() == "Ошибка":
            self.clear()

        bounds = self.current_operand_bounds()
        if bounds:
            start, end = bounds
            operand = self.expression[start:end]
            self.expression = self.expression[:start] + transform(operand) + self.expression[end:]
        else:
            if self.needs_implicit_multiplication():
                self.expression += "*"
            self.expression += fallback
        self.refresh_display()

    def toggle_sign(self):
        if self.input_text.get() == "Ошибка":
            self.clear()

        bounds = self.current_operand_bounds()
        if bounds:
            start, end = bounds
            operand = self.expression[start:end]
            if operand.startswith("-(") and operand.endswith(")"):
                replacement = operand[2:-1]
            elif operand.startswith("-"):
                replacement = operand[1:]
            else:
                replacement = f"-({operand})"
            self.expression = self.expression[:start] + replacement + self.expression[end:]
        elif not self.expression:
            self.expression = "-"
        else:
            self.expression += "-"
        self.refresh_display()

    def toggle_angle_mode(self):
        self.angle_mode.set("RAD" if self.angle_mode.get() == "DEG" else "DEG")

    def clear(self):
        self.expression = ""
        self.input_text.set("0")

    def backspace(self):
        if self.input_text.get() == "Ошибка":
            self.clear()
            return

        self.expression = self.expression[:-1]
        self.refresh_display()

    def calculate(self):
        try:
            result = self.evaluator.evaluate(self.expression)
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("Non-finite result")
            self.expression = self.format_result(result)
            self.input_text.set(self.expression)
        except (ArithmeticError, SyntaxError, ValueError, OverflowError):
            self.expression = ""
            self.input_text.set("Ошибка")

    def refresh_display(self):
        self.input_text.set(self.expression or "0")

    def current_number(self):
        number = []
        for char in reversed(self.expression):
            if char.isdigit() or char == ".":
                number.append(char)
            else:
                break
        return "".join(reversed(number))

    def current_operand_bounds(self):
        expression = self.expression
        if not expression:
            return None

        end = len(expression)
        if expression.endswith("**") or expression[-1] in "+-*/%(":
            return None

        for constant in ("pi", "e"):
            start = end - len(constant)
            if start >= 0 and expression.endswith(constant):
                if start == 0 or not expression[start - 1].isalpha():
                    return start, end

        if expression[-1].isdigit() or expression[-1] == ".":
            start = end - 1
            while start >= 0 and (expression[start].isdigit() or expression[start] == "."):
                start -= 1
            if start >= 0 and expression[start] == "-" and (
                start == 0 or expression[start - 1] in "+-*/%("
            ):
                start -= 1
            return start + 1, end

        if expression[-1] == ")":
            depth = 0
            start = end - 1
            while start >= 0:
                if expression[start] == ")":
                    depth += 1
                elif expression[start] == "(":
                    depth -= 1
                    if depth == 0:
                        function_start = start - 1
                        while function_start >= 0 and expression[function_start].isalpha():
                            function_start -= 1
                        if function_start < start - 1:
                            return function_start + 1, end
                        return start, end
                start -= 1

        return None

    def needs_implicit_multiplication(self):
        if not self.expression:
            return False
        return self.expression[-1] in self.VALUE_END_CHARS or self.expression.endswith(("pi", "e"))

    @staticmethod
    def format_result(value):
        if isinstance(value, int):
            return str(value)

        if math.isclose(value, round(value), rel_tol=0, abs_tol=1e-12):
            return str(int(round(value)))

        return f"{value:.15g}"

    def animate_display_rgb(self):
        hue = (self.rgb_phase % 360) / 360
        glow = self.hsv_to_hex(hue, 1, 1)
        accent = self.hsv_to_hex((hue + 0.5) % 1, 0.85, 1)
        panel = self.hsv_to_hex((hue + 0.08) % 1, 0.65, 0.18)

        self.display_glow.configure(bg=glow)
        self.mode_label.configure(fg=accent, bg=panel)
        self.display.configure(readonlybackground=panel, bg=panel)

        self.rgb_phase = (self.rgb_phase + 4) % 360
        self.root.after(45, self.animate_display_rgb)

    def flash_button(self, text):
        for button in self.buttons.get(text, []):
            self.animate_button_rainbow(button, 0)

    def animate_button_rainbow(self, button, step):
        if step >= len(self.RAINBOW):
            base = self.button_base_styles.get(button)
            if base:
                button.configure(**base)
            return

        color = self.RAINBOW[step]
        button.configure(
            bg=color,
            activebackground=color,
            fg="#050013" if step in {2, 3, 4} else "#ffffff",
        )
        self.root.after(45, lambda: self.animate_button_rainbow(button, step + 1))

    @staticmethod
    def hsv_to_hex(hue, saturation, value):
        red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
        return f"#{round(red * 255):02x}{round(green * 255):02x}{round(blue * 255):02x}"


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
