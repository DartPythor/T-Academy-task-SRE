# Фактор 2: Зависимости (Dependencies)

## Методология 12 Factor App — Фактор II
> Явно объявляйте и изолируйте зависимости.

## Процент выполнения: 70% ⚠️

---

## Что сделано хорошо ✅

1. **Используется Poetry:** Проект имеет `pyproject.toml` с явно указанными зависимостями через `[project]dependencies` и использует `poetry-core` для сборки.

2. **requirements.txt присутствует:** Есть зафиксированный `requirements.txt` со всеми транзитивными зависимостями и точными версиями.

3. **lock-файл Poetry:** Присутствует `poetry.lock`, что гарантирует воспроизводимость зависимостей.

4. **Использование Docker:** образ строится на основе `requirements.txt`, что изолирует зависимости от хост-системы.

5. **Разделение на прямые и транзитивные зависимости:** В `pyproject.toml` перечислены только прямые зависимости, а `requirements.txt` содержит полный граф зависимостей.

6. **Python 3.13:** Используется конкретная мажорная версия Python, что уменьшает риск несовместимости.

---

## Что нужно улучшить 🔧

1. **Отсутствует разделение на dev-зависимости:** В проекте нет инструментов для разработки: тестов (pytest), линтеров (ruff есть в tool, но не как зависимость), type-checker'ов (mypy). Все dev-зависимости не изолированы в `[tool.poetry.group.dev.dependencies]`.

2. **Не настроен менеджер зависимостей Poetry полностью:** В `pyproject.toml` нет секции `[tool.poetry]`, только `[build-system]`. Нет указания `[tool.poetry.dev-dependencies]`.

3. **requirements.txt генерируется не автоматически:** Нет скрипта для регенерации `requirements.txt` из `poetry.lock` при изменении зависимостей.

4. **В Dockerfile используется pip, а не Poetry:** Образ устанавливает зависимости через `pip install -r requirements.txt`, а не через `poetry install`. Это дублирование источников истины.

5. **Нет проверки целостности зависимостей:** Нет `hash`-проверок в requirements.txt (флаг `--require-hashes`).

6. **Frontend-зависимости:** `npm ci` в frontend/Dockerfile может упасть без `package-lock.json`, но есть fallback на `npm install`, что снижает воспроизводимость.

7. **Нет прямых указаний версий Python интерпретатора:** В pyproject.toml указано `^3.13`, но нет проверки соответствия в Dockerfile или CI.

---

## Шаги для улучшения 📋

1. **Добавить dev-зависимости в pyproject.toml:**
   ```toml
   [tool.poetry.group.dev.dependencies]
   pytest = "^8.0"
   pytest-asyncio = "^0.24"
   ruff = "^0.7"
   mypy = "^1.13"
   ```

2. **Настроить Dockerfile для установки через Poetry:**
   ```dockerfile
   COPY pyproject.toml poetry.lock ./
   RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev
   ```

3. **Автоматизировать регенерацию requirements.txt через CI/CD:**
   ```bash
   poetry export -f requirements.txt --output requirements.txt --without-hashes
   ```

4. **Добавить проверку целостности зависимостей:** Использовать `--require-hashes` при установке через pip, или полностью перейти на Poetry в Dockerfile.

5. **Добавить `pip install --no-deps` для избежания конфликтов** при установке Poetry в Docker.

6. **Зафиксировать Node.js версию** в frontend/package.json:
   ```json
   "engines": {
     "node": ">=22.0.0 <23.0.0"
   }
   ```

7. **Добавить проверки в CI:**
   - `poetry check` — проверка pyproject.toml
   - `poetry lock --check` — проверка lock-файла
   - `npm audit` — проверка безопасности frontend-зависимостей