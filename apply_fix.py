#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического исправления asyncio threading ошибки в bot_manager.py
Запуск: python apply_fix.py
"""

import sys
from pathlib import Path

def apply_fixes():
    """Применяет все необходимые исправления к bot_manager.py"""
    
    # Путь к файлу
    file_path = Path("src/telegram/bot_manager.py")
    
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        print("   Убедитесь, что вы запускаете скрипт из корневой директории проекта")
        return False
    
    # Читаем файл
    print(f"📖 Читаем {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Создаём бэкап
    backup_path = file_path.with_suffix('.py.backup')
    print(f"💾 Создаём бэкап: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Применяем исправления
    original_content = content
    changes_count = 0
    
    # FIX 1: Добавляем self.loop = None в __init__
    print("\n🔧 Применяем исправление 1/4: добавление self.loop...")
    old_init = """        self.user_data: Dict[str, dict] = {}
        self.parsing_user_id = None
        
        self._register_handlers()"""
    
    new_init = """        self.user_data: Dict[str, dict] = {}
        self.parsing_user_id = None
        self.loop = None  # FIX: Added event loop attribute
        
        self._register_handlers()"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        changes_count += 1
        print("   ✅ Исправление 1 применено")
    else:
        print("   ⚠️  Исправление 1 уже применено или паттерн не найден")
    
    # FIX 2: Исправляем метод _run_bot
    print("\n🔧 Применяем исправление 2/4: метод _run_bot...")
    old_run_bot = """    def _run_bot(self):
        try:
            self.is_running = True

            
            asyncio.run(self.dp.start_polling(self.bot))
            
        except Exception as e:
            logger.error(f"Ошибка работы Telegram бота: {e}")
            self.is_running = False"""
    
    new_run_bot = """    def _run_bot(self):
        try:
            self.is_running = True
            
            # FIX: Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Run bot
            self.loop.run_until_complete(self.dp.start_polling(self.bot))
            
        except Exception as e:
            logger.error(f"Ошибка работы Telegram бота: {e}")
            self.is_running = False
        finally:
            if self.loop and not self.loop.is_closed():
                self.loop.close()"""
    
    if old_run_bot in content:
        content = content.replace(old_run_bot, new_run_bot)
        changes_count += 1
        print("   ✅ Исправление 2 применено")
    else:
        print("   ⚠️  Исправление 2 уже применено или паттерн не найден")
    
    # FIX 3: Исправляем _send_startup_notification
    print("\n🔧 Применяем исправление 3/4: метод _send_startup_notification...")
    old_notification = """            # Запускаем в новом цикле событий
            asyncio.run(send_and_close())"""
    
    new_notification = """            # FIX: Use new event loop instead of asyncio.run()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send_and_close())
            finally:
                loop.close()"""
    
    if old_notification in content:
        content = content.replace(old_notification, new_notification)
        changes_count += 1
        print("   ✅ Исправление 3 применено")
    else:
        print("   ⚠️  Исправление 3 уже применено или паттерн не найден")
    
    # FIX 4: Исправляем метод stop
    print("\n🔧 Применяем исправление 4/4: метод stop...")
    old_stop = """            # 🚀 non-blocking stop
            if hasattr(self, 'dp') and self.dp and self.dp._loop and not self.dp._loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.dp.stop_polling(), self.dp._loop)"""
    
    new_stop = """            # FIX: Stop polling using our loop
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.dp.stop_polling(), self.loop)"""
    
    if old_stop in content:
        content = content.replace(old_stop, new_stop)
        changes_count += 1
        print("   ✅ Исправление 4 применено")
    else:
        print("   ⚠️  Исправление 4 уже применено или паттерн не найден")
    
    # Проверяем, были ли изменения
    if content == original_content:
        print("\n⚠️  Никаких изменений не было сделано.")
        print("   Возможно, исправления уже применены или структура файла изменилась.")
        return False
    
    # Сохраняем исправленный файл
    print(f"\n💾 Сохраняем исправленный файл...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Успешно применено {changes_count} исправлений!")
    print(f"   Бэкап сохранён: {backup_path}")
    print(f"\n🚀 Теперь можете запустить: uv run python bot.py")
    
    return True

def restore_backup():
    """Восстанавливает файл из бэкапа"""
    file_path = Path("src/telegram/bot_manager.py")
    backup_path = file_path.with_suffix('.py.backup')
    
    if not backup_path.exists():
        print(f"❌ Бэкап не найден: {backup_path}")
        return False
    
    print(f"♻️  Восстанавливаем из бэкапа: {backup_path}")
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Файл восстановлен из бэкапа")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Скрипт исправления asyncio threading в bot_manager.py")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        # Восстанавливаем из бэкапа
        restore_backup()
    else:
        # Применяем исправления
        success = apply_fixes()
        
        if success:
            print("\n" + "=" * 60)
            print("💡 Совет: если что-то пошло не так, запустите:")
            print("   python apply_fix.py --restore")
            print("=" * 60)
        else:
            sys.exit(1)
