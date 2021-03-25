import sys
import traceback
from time import sleep

from mcrcon import MCRcon
from phue import Bridge

is_light_changed = False  # Изменялось ли нами состояние лампочки
ttime = 1  # Время плавного перехода в десятых долях секунды
bridge_request_timeout = 0.03 # 3 сотых секунды между запросами к мосту, тк он может обрабатывать не более 30 запросов в секунду

#Проверяем наличие файла и если он есть, берём оттуда данные
try:
    f = open("config.txt", "r")
    config = f.read()
    config = config.splitlines()
    f.close()
    foo = 0
except:
    f = open("config.txt", "w")
    foo = 1
    print('Сейчас вы должны ввести свои данные, но один раз, при следующих запусках оно спрашиваться не будет. Если вы захотите позже изменить данные, то либо удалите config.txt или сами его отредачите')

try:  # Для обработки исключений используем try
    # Просим ввести айпи моста филипс (если есть конфиг, то оттуда загружаемся)
    if foo:
        bridge_ip = input('Введите IP моста: ')
    else:
        bridge_ip = config[0]
        print('Айпи моста филипс загрузился из файла')
    
    # Подключаемся к мосту (если это происходи в первый раз, на мосте надо нажать кнопку)
    b = Bridge(bridge_ip)  # Инициализация объекта моста
    b.connect()  # Коннект к мосту
    print('Connected')  # Если успешно, сообщаем пользователю о том, что подключились
    
    # Просим ввести номер лампочки (как правило это 1) (если есть конфиг, то оттуда загружаемся)
    if foo:
        light_id = int(input('Введите номер лампочки: '))
    else:
        light_id = int(config[1])
        print('Номер лампочки загрузился из файла')
    
    lights = b.lights  # Получаем список лампочек
    light1_state = b.get_light(light_id, 'on')  # Запоминаем исходное состояние лампочки (вкл или выкл)
    sleep(bridge_request_timeout) # Выжидаем таймаут перед следующим запросом, тк мост может обрабатывать не более 30 запросов в секунду
    b.set_light(light_id, 'on', True)  # Включаем лампочку
    is_light_changed = True  # Тк мы включили лампочку, которая могла быть выключена, is_light_changed меняем на True
    sleep(bridge_request_timeout) # Выжидаем таймаут перед следующим запросом, тк мост может обрабатывать не более 30 запросов в секунду
    light_brightness = b.get_light(light_id, 'bri')  # Запоминаем яркость лампочки

    # Получаем от пользователя данные для подключеняи к серверу и ваш ник: (если есть конфиг, то оттуда загружаемся)
    if foo:
        rcon_ip = input('Введите rcon-ip сервера: ')
        rcon_port = int(input('Введите rcon-порт сервера: '))
        rcon_pass = input('Введите rcon-пароль сервера: ')
        player_name = input('Введите ник игрока: ')
        config = [bridge_ip, str(light_id), rcon_ip, str(rcon_port), rcon_pass, player_name]
        bar = ""
        for i in config:
            bar += i + "\n"
        f.write(bar)
        f.close()
        print('Всё сохранилось в файл')
    else:
        rcon_ip = config[2]
        rcon_port = int(config[3])
        rcon_pass = config[4]
        player_name = config[5]
        print('Данные для подключеняи к серверу и ваш ник загрузились из файла')

    # Начинаем выполнение программы после нажатия ENTER
    input('Для старта нажмите ENTER...')

    # Пока программа не будет завершена пользователем (вечный цикл)...
    while True:
        # Отправляем на сервер майнкрафта запрос в виде команды нашего плагина и нашего ника
        with MCRcon(rcon_ip, rcon_pass, rcon_port) as mcr:
            resp = mcr.command("lightsync " + player_name)  # Ответ будет сохранен в переменную resp типа String

            if (resp == 'E1\n') or (resp == 'E0\n'):  # Если в resp окажется код ошибки...
                print('\nгрок не находится на сервере или никнейм введен с ошибкой')  # Выдаем сообщение пользователю
                input()  # Даем пользователю прочитать сообщение об ошибке, и после нажатия любой кнопки...
                break  # выходим из цикла, после чего программа будет завершена

            mc_lighlevel = int(
                resp)  # Если в ответе нет кода ошибки, значит мы получили степень освещенности. Переводим значением в числовой тип данных.
            print('\rMinecraft lightlevel is: ' + str(mc_lighlevel) + ' ',
                  end='')  # Вместо предыдущей строки с уровнем освещенности выдаем новую
            # Алгоритм, описанный в видео:

            if (mc_lighlevel < 5) and b.get_light(light_id, 'on'):
                b.set_light(light_id, 'on', False, transitiontime=ttime)
            elif mc_lighlevel >= 5:
                if not b.get_light(light_id, 'on'):
                    b.set_light(light_id, 'on', True, transitiontime=ttime)
                b.set_light(light_id, 'bri', int((mc_lighlevel - 5) * 25.4), transitiontime=ttime)
            # Выжидаем таймаут перед следующим запросом, тк мост может обрабатывать не более 30 запросов в секунду
            sleep(bridge_request_timeout)

except KeyboardInterrupt:  # Исключение, появляющееся при закрытии пользователем программы
    print("\rFinished by user")
    input()

except:  # При других ошибках выдаем отчет о них
    print("Error ocured")
    print("=====ERROR REPORT INFO=====")
    traceback.print_exc(limit=2, file=sys.stdout)
    print("=====END OF REPORT=====")
    input()

finally:  # Если мы меняли состояние лампочек, возвращаем их значения на исходную
    try:
        if is_light_changed:
            b.set_light(light_id, 'on', True)  # Включаем лампочку...
            b.set_light(light_id, 'bri', light_brightness)  # Чтобы выставить на ней исходную яркость
            b.set_light(light_id, 'on',
                        light1_state)  # Далее переводим лампочку во Вкл или Выкл в зависимости от того, что было на старте
    except:
        pass  # Если во время попытки возврата исходного состояния лампочек произойдет ошибка, просто игнорируем это
