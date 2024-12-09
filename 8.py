import random
import customtkinter as ctk
import matplotlib.pyplot as plt
from tkinter import messagebox


# Базовый класс игры
class BaseGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        raise NotImplementedError("Этот метод должен быть переопределён в наследуемом классе.")

    def check_guess(self, guess):
        raise NotImplementedError("Этот метод должен быть переопределён в наследуемом классе.")


# Логика игры (наследуется от BaseGame)
class GameLogic(BaseGame):
    def __init__(self):
        super().__init__()

    def reset_game(self):
        """Сбрасывает игру для нового раунда."""
        self.target_number = random.randint(1, 100)
        self.attempts = 0
        self.history = []  # Список для хранения истории попыток

    def check_guess(self, guess):
        """Проверяет введённое число и возвращает подсказку."""
        self.attempts += 1
        difference = abs(self.target_number - guess)
        if guess == self.target_number:
            result = "win"
        elif difference <= 5:
            result = "🔥 Очень горячо!"
        elif difference <= 10:
            result = "🌡️ Горячо."
        elif difference <= 20:
            result = "☀️ Тепло."
        else:
            result = "❄️ Холодно."
        self.history.append((guess, result))  # Сохраняем введённое число и подсказку
        return result

    def save_game_log(self):
        """Сохраняет результаты игры в файл."""
        with open("game_log.txt", "a") as log_file:
            log_file.write(f"Число: {self.target_number}, Попытки: {self.attempts}\n")

    def generate_closeness_chart(self):
        """Создаёт и сохраняет график близости к загаданному числу."""
        attempts = list(range(1, len(self.history) + 1))
        differences = [abs(guess - self.target_number) for guess, _ in self.history]

        plt.figure(figsize=(8, 5))
        plt.plot(attempts, differences, marker='o', linestyle='-', color='orange', label='Разница до загаданного числа')
        plt.axhline(y=0, color='green', linestyle='--', label='Загаданное число угадано')
        plt.xlabel('Номер попытки')
        plt.ylabel('Отклонение от загаданного числа')
        plt.title('График близости к загаданному числу')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        plt.savefig('closeness_chart.png')
        plt.close()


# Окно с победой
class WinWindow(ctk.CTkToplevel):
    def __init__(self, master=None, target_number=None, attempts=None):
        super().__init__(master)
        self.master = master
        self.target_number = target_number
        self.attempts = attempts
        self.title("Поздравляем!")
        self.geometry("400x300")
        self.create_widgets()
        self.grab_set()

    def create_widgets(self):
        """Создаёт элементы интерфейса для окна победы."""
        self.label_title = ctk.CTkLabel(
            self, text="Поздравляем!", font=ctk.CTkFont(size=24, weight="bold"), text_color="green"
        )
        self.label_title.pack(pady=20)

        self.label_message = ctk.CTkLabel(
            self,
            text=f"Вы угадали число {self.target_number}!\n"
                 f"Количество попыток: {self.attempts}",
            font=ctk.CTkFont(size=18),
            text_color="white"
        )
        self.label_message.pack(pady=10)

        self.button_close = ctk.CTkButton(
            self, text="Закрыть", font=ctk.CTkFont(size=16), command=self.close_window
        )
        self.button_close.pack(pady=20)

    def close_window(self):
        """Закрывает окно победы."""
        self.destroy()


# Основное окно игры
class GameUI(ctk.CTk):
    def __init__(self, game_logic):
        super().__init__()
        self.game_logic = game_logic
        self.title("Горячо-Холодно")
        self.geometry("700x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()
        self.bind("<Return>", self.handle_enter_key)  # Привязка клавиши Enter

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(
            self, text="Угадайте число от 1 до 100", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_title.pack(pady=10)

        self.entry_guess = ctk.CTkEntry(self, placeholder_text="Введите число", font=ctk.CTkFont(size=18))
        self.entry_guess.pack(pady=10)

        self.button_check = ctk.CTkButton(
            self, text="Проверить", font=ctk.CTkFont(size=16), command=self.check_guess
        )
        self.button_check.pack(pady=10)

        self.button_reset = ctk.CTkButton(
            self, text="Сбросить", font=ctk.CTkFont(size=16), command=self.reset_game
        )
        self.button_reset.pack(pady=10)

        self.history_textbox = ctk.CTkTextbox(self, width=600, height=200)
        self.history_textbox.pack(pady=10)

        self.button_rules = ctk.CTkButton(
            self, text="Правила", font=ctk.CTkFont(size=16), command=self.open_rules
        )
        self.button_rules.pack(pady=10)

    def handle_enter_key(self, event):
        self.check_guess()

    def check_guess(self):
        try:
            guess = int(self.entry_guess.get())
            result = self.game_logic.check_guess(guess)
            self.update_history()
            self.entry_guess.delete(0, "end")

            if result == "win":
                self.game_logic.save_game_log()
                self.game_logic.generate_closeness_chart()
                self.open_win_window()
        except ValueError:
            self.entry_guess.delete(0, "end")

    def reset_game(self):
        self.game_logic.reset_game()
        self.update_history()

    def update_history(self):
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        for i, (guess, result) in enumerate(self.game_logic.history, start=1):
            self.history_textbox.insert("end", f"Попытка №{i}: {guess} → {result}\n")
        self.history_textbox.configure(state="disabled")

    def open_rules(self):
        RulesWindow(self)

    def open_win_window(self):
        win_window = WinWindow(self, target_number=self.game_logic.target_number, attempts=self.game_logic.attempts)
        win_window.mainloop()


# Окно с правилами
class RulesWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Правила игры")
        self.geometry("500x400")
        self.create_widgets()
        self.grab_set()

    def create_widgets(self):
        self.rules_textbox = ctk.CTkTextbox(self, width=450, height=250)
        self.rules_textbox.pack(pady=10)
        rules = (
            "1. Компьютер загадывает число от 1 до 100.\n"
            "2. Введите число и нажмите 'Проверить'.\n"
            "3. Подсказки: 🔥, 🌡️, ☀️, ❄️.\n"
        )
        self.rules_textbox.insert("1.0", rules)
        self.rules_textbox.configure(state="disabled")


class HotColdGameApp:
    def run(self):
        game_ui = GameUI(GameLogic())
        game_ui.mainloop()


if __name__ == "__main__":
    app = HotColdGameApp()
    app.run()
