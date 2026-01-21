import curses


class InputWindow:  # Позиция x, позиция y, ширина, высота, текст окна.
    def __init__(self, position_x, position_y, width, heigth, text="", xMax=0):
        self.x = position_x

        self.y = position_y

        self.w = width

        self.h = heigth

        self.t = text

        self.inputwin = curses.newwin(
            self.h - 2, self.w - 3, self.y + 1, self.x + 2
        )  # Разметка окна ввода

        self.win = curses.newwin(
            self.h, self.w, self.y, self.x
        )  # Основное окно с рамкой

        self.xMax = xMax

    def draw(self):
        # Главное окно

        self.win.border()  # Рамка

        self.win.addstr(0, 1, self.t)  # Надпись на окне(не более 8 символов)

        self.win.refresh()

        self.inputwin.refresh()

    def edit(self):  # Статическое окно
        input = self.inputwin  # Окно ввода

        input.clear()

        text = ""  # Возвращаемый текст

        cursX = 0  # Позиция курсора

        while True:
            # Каждую итерацию цикла отрисовываем окно, ждем ввод, в зависимости от ввода делаем действие

            input.addstr(0, 0, text)

            input.move(0, cursX)

            self.win.refresh()

            self.inputwin.refresh()

            ch = input.getch()

            if ch == 7:  # Проверяем на Ctrl+g
                return text

            elif ch == 10:  # Проверям на enter
                return text

            elif cursX > self.w - 5:
                StaticWindow(1, 0, f"Maximum lenght {self.w - 4}")

            elif ch == 127:  # Проверяем на backspace
                if text != "":
                    text = text[:-1]

                    cursX -= 1

                    input.clear()

                    input.refresh()

            else:  # Отрисосвываем текст
                text += chr(ch)

                cursX += 1

    def editResize(self):  # Динамически масштабируемое окно
        input = self.inputwin  # Окно ввода

        input.clear()

        text = ""  # Возвращаемый текст

        cursX = 0  # Позиция курсора

        while True:
            # Каждую итерацию цикла отрисовываем окно, ждем ввод, в зависимости от ввода делаем действие

            input.addstr(0, 0, text)

            input.move(0, cursX)

            self.win.refresh()

            self.inputwin.refresh()

            ch = input.getch()

            if ch == 7:  # Проверяем на Ctrl+g
                return text

            elif ch == 10:  # Проверям на enter
                return text

            elif ch == 127:  # Проверяем на backspace
                if text != "":
                    text = text[:-1]

                    cursX -= 1

                    input.clear()

                    input.refresh()

            elif len(text) <= (self.xMax - 6):  # Отрисосвываем текст
                text += chr(ch)

                cursX += 1

            if cursX > self.w - 4:  # Динамическое увеличение рамки и текстового поля
                self.x -= 1

                self.w += 2

                input.mvwin(self.y + 1, self.x + 2)

                self.win.mvwin(self.y, self.x)

                input.resize(self.h - 2, self.w - 3)  # Разметка окна ввода

                self.win.resize(self.h, self.w)  # Основное окно с рамкой

                self.win.border()

                self.win.addstr(0, 1, self.t)  # Надпись на окне(не более 8 символов)

    def clear(self):
        self.inputwin.clear()

        self.inputwin.refresh()


class StaticWindow:  # Поция x, позиция y, текст
    def __init__(self, position_x, position_y, text, textInline="", reverse=False):
        self.x = position_x

        self.y = position_y

        if len(text) < 20:
            self.w = 24

        else:
            self.w = len(text) + 4

        self.h = 3

        self.t = text

        self.ti = textInline

        self.r = reverse

        self.win = curses.newwin(self.h, self.w, self.y, self.x)

    def draw(self):
        if self.r:
            self.win.attron(curses.A_REVERSE)

            self.win.border()

            self.win.attroff(curses.A_REVERSE)

            self.win.attron(curses.A_REVERSE)

            self.win.addstr(0, 1, self.ti)

            self.win.attroff(curses.A_REVERSE)

        else:
            self.win.border()

            self.win.addstr(0, 1, self.ti)

        self.win.addstr(1, 2, self.t)

        self.win.refresh()

    def clear(self):
        self.win.clear()

        self.win.refresh()
