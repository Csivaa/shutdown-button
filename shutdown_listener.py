#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shutdown_listener.py
====================
Слушает последовательный порт Arduino Uno и выключает компьютер,
когда с платы приходит строка "PRESS" (кнопка нажата).

Работает на Windows, Linux и macOS.

Перед первым запуском установите библиотеку pyserial:
    pip install pyserial
"""

import os
import sys
import time
from datetime import datetime

# ------------------------------ НАСТРОЙКИ ------------------------------
PORT_NAME = "AUTO"      # "AUTO" — искать порт автоматически; или укажите явно, например "COM3"
BAUDRATE = 9600         # должно совпадать со скоростью в скетче Arduino
SHUTDOWN_DELAY_SEC = 5  # задержка перед выключением (можно отменить: Win+R -> shutdown /a)
# -----------------------------------------------------------------------

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown_listener.log")


def log(message):
    """Печатает сообщение в консоль и дописывает его в журнал рядом со скриптом."""
    line = "[%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


try:
    import serial
    from serial.tools import list_ports
except ImportError:
    log("ОШИБКА: не установлена библиотека pyserial. Установите её командой:  pip install pyserial")
    sys.exit(1)


def find_arduino_port():
    """Ищет COM-порт, похожий на Arduino (по описанию устройства)."""
    ports = list(list_ports.comports())
    for port in ports:
        desc = ((port.description or "") + " " + (port.manufacturer or "")).lower()
        if any(key in desc for key in ("arduino", "ch340", "ch9102", "ft232", "usb serial", "usb-serial")):
            return port.device
    if ports:  # ничего похожего не нашли — берём первый доступный порт
        return ports[0].device
    return None


def shutdown_pc():
    """Выключает компьютер."""
    log("Кнопка нажата! Выключение через %d сек." % SHUTDOWN_DELAY_SEC)
    if os.name == "nt":  # Windows
        os.system('shutdown /s /t %d /c "Кнопка выключения нажата"' % SHUTDOWN_DELAY_SEC)
    elif sys.platform.startswith("linux"):
        os.system("shutdown -h now")
    elif sys.platform == "darwin":  # macOS
        os.system("osascript -e 'tell app \"System Events\" to shut down'")
    else:
        log("Неизвестная операционная система: выключение не выполнено.")


def main():
    log("Слушатель кнопки выключения запущен.")
    port_name = PORT_NAME if PORT_NAME != "AUTO" else None

    while True:
        if not port_name:
            port_name = find_arduino_port()
            if not port_name:
                log("Arduino не найдена. Повторная попытка через 5 секунд...")
                time.sleep(5)
                continue
            log("Найден порт: %s" % port_name)

        try:
            with serial.Serial(port_name, BAUDRATE, timeout=1) as ser:
                ser.reset_input_buffer()
                log("Слушаю порт %s (скорость %d). Нажмите кнопку на макете." % (port_name, BAUDRATE))
                while True:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        log("Arduino: %s" % line)
                    if line == "PRESS":
                        shutdown_pc()
                        return 0
        except serial.SerialException as e:
            log("Ошибка порта %s: %s" % (port_name, e))
            log("Повторная попытка через 5 секунд. (Закройте Serial Monitor и Arduino IDE, если они открыты.)")
            port_name = None
            time.sleep(5)
        except KeyboardInterrupt:
            log("Остановлено пользователем (Ctrl+C).")
            return 0


if __name__ == "__main__":
    sys.exit(main())
