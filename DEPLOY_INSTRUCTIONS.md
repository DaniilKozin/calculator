# 🚀 Инструкция по деплою на GitHub и Streamlit Cloud

## Шаг 1: Подготовка к загрузке на GitHub

### 1.1 Инициализация Git репозитория (если еще не сделано)

```bash
# Перейдите в папку проекта
cd "/Users/daniilkozin/Library/Application Support/Zenex Calc"

# Инициализируйте Git репозиторий
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "Initial commit: Zenex RevShare Pool Calculator"
```

### 1.2 Создание репозитория на GitHub

1. Перейдите на [GitHub](https://github.com)
2. Нажмите "New repository"
3. Название: `calculator`
4. Описание: `Zenex RevShare Pool Calculator - Interactive dashboard for analyzing pool returns`
5. Выберите "Public" (для бесплатного Streamlit Cloud)
6. НЕ добавляйте README, .gitignore или LICENSE (они уже есть)
7. Нажмите "Create repository"

### 1.3 Подключение к GitHub

```bash
# Добавьте удаленный репозиторий
git remote add origin https://github.com/DaniilKozin/calculator.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

## Шаг 2: Деплой на Streamlit Cloud

### 2.1 Подключение к Streamlit Cloud

1. Перейдите на [share.streamlit.io](https://share.streamlit.io)
2. Войдите через GitHub аккаунт
3. Нажмите "New app"

### 2.2 Настройка приложения

- **Repository**: `DaniilKozin/calculator`
- **Branch**: `main`
- **Main file path**: `dashboard_app.py`
- **App URL**: выберите уникальное имя (например: `zenex-calculator`)

### 2.3 Деплой

1. Нажмите "Deploy!"
2. Дождитесь завершения сборки (2-3 минуты)
3. Приложение будет доступно по URL: `https://zenex-calculator.streamlit.app`

## Шаг 3: Проверка и настройка

### 3.1 Проверка работоспособности

- ✅ Приложение загружается без ошибок
- ✅ Все графики отображаются корректно
- ✅ Параметры можно изменять через UI
- ✅ Данные экспортируются в CSV

### 3.2 Обновления

При изменении кода:
```bash
git add .
git commit -m "Update: описание изменений"
git push
```

Streamlit Cloud автоматически обновит приложение в течение 1-2 минут.

## 🔒 Безопасность

✅ **Все настроено безопасно:**
- Чувствительные данные исключены из репозитория
- `.gitignore` настроен правильно
- Конфигурация Streamlit оптимизирована
- Сбор статистики отключен

## 📊 Мониторинг

Streamlit Cloud предоставляет:
- Логи приложения
- Метрики использования
- Статистику ошибок
- Управление ресурсами

## 🆘 Решение проблем

### Ошибка при сборке
- Проверьте `requirements.txt`
- Убедитесь, что `dashboard_app.py` в корне репозитория

### Приложение не загружается
- Проверьте логи в Streamlit Cloud
- Убедитесь, что все зависимости установлены

### Медленная работа
- Оптимизируйте код (кэширование)
- Уменьшите размер данных

---

**Готово! 🎉** Ваше приложение теперь доступно онлайн и будет автоматически обновляться при изменениях в GitHub.