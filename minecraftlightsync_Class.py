import sys
import traceback
from time import sleep
from inspect import currentframe, getframeinfo

from mcrcon import MCRcon
from phue import Bridge, Light
import re


class MinecraftLightSync:
    """
        ### MinecraftLightSync

            :param bool `light_status`: Состояние лампочки 
            :default = False:

            :param float `transition_time`: Время для изменения уровня яркости 
            :default = 1.0: каждые `transition_time` / 10 секунд изменяется яркость
                `transition_time` = 3
                Пример у лампочки на данные момент яркость  "X"-100%
                Приходит запрос на изменение на яркость     "Y"- 33%
                Изменение яркости в таком ввиде будет происходить так
                `transition_time` / 10
                100 -> 66 -> 33

            :param float `bridge_request_timeout`: Время ожидания между запросами к мосту лампочки
            :default = 0.03: секунды между запросами, 30 запросов в секунду нижний предел

            :param bool `strict`: Строгое выполнение
            :default = False: Работа с ошибками, попытки переподключения и т.д
    """
    strict: bool  # Строгое выполнение

    lights_status: bool  # Изменялось ли нами состояние лампочки
    transition_time: float  # value -> value / 10, одна десятая если не понял, отправляешь только value
    lights_state: list  # Исходные состояния лампочек

    bridge_request_timeout: float # Class.request -> Bridge TIMEOUT, Class.request ...
    bridge_ip: str  # IP-адресс Моста
    bridge_instance: Bridge  # Инстанс моста

    rcon_ip:str  # rcon IP str
    rcon_port:int  # rcon PORT str
    rcon_pass:str  # rcon Пароль  str
    player_name:str  # Имя игрока в майнкрафте
    player_find_attemps:int # Кол-во попыток найти игрока на сервере

    ip_pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

    minecraft_errors: list  # Ошибки RCON

    def __init__(self, rcon_ip="", rcon_port=0, rcon_pass="", player_name="", bridge_ip="", light_status=False, transition_time=1, bridge_request_timeout=0.03, strict=False):
        #  Вставка базовых значений
        self.light_status = light_status
        self.transition_time = transition_time
        self.bridge_request_timeout = 0.03 if bridge_request_timeout < 0.03 else bridge_request_timeout  # Не может быть меньше 0.03
        self.minecraft_errors = ["E1", "E0"]
        self.player_find_attemps = 0

        #  Проверки
        self.rcon_ip = self.validate(rcon_ip, "ip", "rcon-ip")
        self.rcon_port = self.validate(rcon_port, "port", "rcon-port")
        self.player_name = self.validate(player_name, "name", "player-name")
        self.bridge_ip = self.validate(bridge_ip, "ip", "bridge-ip")
        self.rcon_pass = rcon_pass
        self.bridge_instance = self.get_bridge(self.bridge_ip)

        #  Начинаем выполнение программы после нажатия ENTER
        input('Для старта нажмите ENTER...')
        try:
            self.get_lights_state()
            self.pool(endless=True)
        except KeyboardInterrupt:  # DEPRICATED DELETE THIS. ITS BAD
            print("\rFinished by user")  # DEPRICATED DELETE THIS. ITS BAD
            exit()  # DEPRICATED DELETE THIS. ITS BAD
        except Exception as e:
            self.error_hanlder(e, 72)
        finally:   # Если мы меняли состояние лампочек, возвращаем их значения на исходную
            self.regenerate()

    def error_hanlder(self, description: str, line:int, force=False):
        """Обработчик ошибок чтобы получить строку используйте `getframeinfo(currentframe()).lineno`"""
        text = f"У нас ошибка\nОписание: {description}\nФайл: {__file__}\nСтрока: {line}"
        if force:
            raise EnvironmentError(text)
        print("Error ocured")
        print("===========ERROR INFO REPORT======")
        print(text)
        print("=======END ERROR INFO REPORT======")
        print("\n")

    def get_bridge(self, ip: str, username=None, config_file_path=None):
        """
            Получение объекта моста
                :param str `ip`: IP адресс моста в виде "192.168.1.100"
                :param str `username`: Пользователь str !!!не обязетальный параметр!!!
                :param str `config_file_path`: Путь к файлу конфига !!!не обязетальный параметр!!!
                :return Bridge: Инстанс объекта моста
        """
        # Создание объекта моста
        # Подключение УЖЕ ЕСТЬ внутри функции поэтому она не обязательна
        attempts = 0
        connected = False
        while not connected and attempts < 6:
            try:
                bridge_object = Bridge(ip=ip, username=username, config_file_path=config_file_path)
                connected = True
                print(f"Успешно подключено  IP-адрес: {ip}")
            except ConnectionRefusedError:
                attempts += 1  # Попытка номер {attemps}
                print(
                    f"""
                    Не правильно указан IP-адрес или нет подключение к лампочке
                    IP-был: {ip}
                    Попыток {6 - attempts}
                    Можете поменять IP, username (Оставьте пустым если не хотите)
                    """
                )
                input_ip = input("IP: ")  # Новые ip
                input_user = input("Username: ")  # Новые user
                ip = ip if input_ip == "" else input_ip  # Не менять если пусто
                username = username if input_user == "" else input_user  # Не менять если пусто
        if not (connected and attempts < 6):
            self.error_hanlder(
                "Слишком много попыток подключения к Мосту",
                getframeinfo(currentframe()).lineno,
                force=True
            )
        return bridge_object

    def get_lights_state(self):
        """Получаем и сохроняем состояние лампочек, прошлые значения стираются"""
        self.lights_state.clear()
        light: Light
        for light in self.bridge_instance.lights:
            self.lights_state.append((light.on, light.brightness))  # Запоминаем включена ли лампочка или выключена
        sleep(self.bridge_request_timeout)  # Выжидаем таймаут перед следующим запросом, тк мост может обрабатывать не более 30 запросов в секунду

    def set_lights(self, minecraft_light_level:int):
        """
            Проводим циклом по лампочкам и ставим яркость
                :param int `minecraft_light_level`: - яркость в майнкрафте"""
        light: Light
        for light in self.bridge_instance.lights:
            light.transitiontime = int(round(self.transition_time))  # В файле библиотеки обязателен int = Это время изменения
            #  Уровень яркости в майне       Включена ли лампочка
            if minecraft_light_level < 5 and light.on:
                light.on = False  # Вырубаем лампочку ибо темно да и она включена
            elif minecraft_light_level >= 5:
                if light.on is False:  # Лампа выключена?
                    light.on = True  # Включаем лампочку
                light.brightness = int((minecraft_light_level - 5) * 25.4)  # Ставим яркость
            print(f"Сейчас яркость равна {int((minecraft_light_level - 5) * 25.4)}")
        sleep(self.bridge_request_timeout)  # Выжидаем таймаут перед следующим запросом, тк мост может обрабатывать не более 30 запросов в секунду

    def regenerate(self):
        """Проводим циклом по лампочкам и возвращаем все на исходную"""
        light: Light
        for index, light in self.bridge_instance.lights:
            light.on = self.lights_state[index][0]
            light.brightness = self.lights_state[index][1]

    def validate(self, value, mode:str, target=""):
        "Валидатор имен, Ip, port"
        completed = False
        while not completed:
            if mode == "name":
                self.player_find_attemps = 0
                if value != "":
                    completed = True
                    print(f"{target}: OK, {value}")
                else:
                    print(f"{target}: не валидно, {value}")
            elif mode == "ip":
                if re.fullmatch(self.ip_pattern, value) is not None:
                    completed = True
                    print(f"{target} ok, {value}")
                else:
                    print(f"{target} не валидно, {value}")
            elif mode == "port":
                if int(value) >= 0:
                    completed = True
                    print(f"{target} port ok, {value}")
                else:
                    print(f"{target} port не валидно, {value}")
            if not completed:
                value = input(f"Введите {target}: ")
        return str(value)

    def pool(self, endless:bool):
        "Запускаем основную часть класса, даем запросы в RCON и отдаем в лампочки"
        # Пока программа не будет завершена пользователем (вечный цикл)...
        while True if not endless else endless:
            # Отправляем на сервер майнкрафта запрос в виде команды нашего плагина и нашего ника
            with MCRcon(self.rcon_ip, self.rcon_pass, self.rcon_port) as mcr:
                response = mcr.command("lightsync " + self.player_name).strip() # Ответ будет сохранен в переменную resp типа String
                if response in self.minecraft_errors:  # Если в response окажется код ошибки...
                    self.player_find_attemps += 1  #  Не могу найти пользователя
                    if self.player_find_attemps < 2:  # Два раза не могу найти прошу пользователя вбить новые данные
                        print("Не могу найти игрока на сервере")
                        self.player_name = self.validate("", "name", "player_name")
                else:
                    self.player_find_attemps = 0  # Сброс счетчика
                    minecraft_light_level = int(response)  # Уровень яркости в майнкрафте
                    self.set_lights(minecraft_light_level)  # Ставим яркость



# Говорит питону что этот скрипт запущен самостоятельно python3 minecraftlightsync.py
if __name__ == "__main__":
    print("Файл запущен не в виде модуля")
    rcon_ip = input("Введите RCON-ip: ")
    rcon_port = input("Введите RCON-port: ")
    rcon_pass = input("Введите RCON-pass: ")
    player_name = input("Введите ник пользователя: ")
    bridge_ip = input("Введите ip моста: ")


    # Запуск
    MinecraftLightSync(
        rcon_ip=rcon_ip,
        rcon_port=rcon_port,
        rcon_pass=rcon_pass,
        player_name=player_name,
        bridge_ip=bridge_ip,
    )
