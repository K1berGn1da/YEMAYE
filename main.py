import tkinter as tk
from tkinter import font
class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.expression = ""
        self.input_text = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Дисплей
        display_frame = tk.Frame(self.root, bg="#222")
        display_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        display = tk.Entry(display_frame, textvar=self.input_text,
                           font=("Arial", 24), justify="right",
                           bg="#222", fg="#fff", bd=0)
        display.pack(fill=tk.BOTH, ipady=20)

        # Кнопки
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['C', '√', '%', '←']
        ]

        for row in buttons:
            row_frame = tk.Frame(buttons_frame)
            row_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            for btn_text in row:
                self.create_button(row_frame, btn_text)

    def create_button(self, parent, text):
        colors = {
            '/': '#ff9500', '*': '#ff9500', '-': '#ff9500', '+': '#ff9500', '=': '#34c759',
            'C': '#ff3b30', '√': '#5ac8fa', '%': '#5ac8fa', '←': '#ff3b30'
        }

        btn = tk.Button(parent, text=text, font=("Arial", 18),
                        bg=colors.get(text, "#fff"),
                        fg="#000" if text not in ['/', '*', '-', '+', '=', 'C', '←'] else "#fff",
                        command=lambda: self.on_button_click(text),
                        relief=tk.FLAT, bd=0)
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
            self.input_text.set("")
        elif char == '=':
            try:
                result = eval(self.expression)
                self.input_text.set(result)
                self.expression = str(result)
            except:
                self.input_text.set("Ошибка")
                self.expression = ""
        elif char == '←':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif char == '√':
            try:
                result = float(self.expression) ** 0.5
                self.input_text.set(result)
                self.expression = str(result)
            except:
                self.input_text.set("Ошибка")
        else:
            self.expression += char
            self.input_text.set(self.expression)


if __name__ == "__main__":
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()