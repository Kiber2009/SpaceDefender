# Space Defender
## О проекте
Space Defender - Игра наподобие Space Invaders
### Использованные библиотеки
* Python 3.11.5
* Pygame
* PyInstaller
### Скачивание и использование
* Загрузите последнюю версию Space Defenders
* Извлеките содержимое версии игры в любое удобное место. _Например `C:\Space Defenders`_
* Для запуска найдите приложение main.exe и запустите его. _например `C:\Space Defenders\main.exe`_
## Сборка из исходного кода
* Вам понадобится Python 3.11 или более поздней версии
* Клонируйте репозиторий:
    ```shell
    git clone https://github.com/Kiber2009/SpaceDefenders.git
    cd SpaceDefenders
    ```
* Выполните `python -m pip install -r requirements.txt` для установки всех необходимых библиотек.
* Соберите приложение
    ```shell
    pyinstaller --onefile --noconsole main.py -i data/icon.ico
    ```