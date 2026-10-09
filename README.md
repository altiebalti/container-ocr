# container-ocr

Лаба 2 з хмарних обчислень: розпізнавання номера вантажного контейнера з фото через Google Cloud Vision API.

Фото йде на Cloud Run (FastAPI), той викликає Vision (`TEXT_DETECTION`), шукає в тексті номер за ISO 6346,
перевіряє контрольну цифру і пише результат у Firestore, а фото в Cloud Storage. Є сторінка, яка на телефоні
відкриває камеру, і Swagger на `/docs`.

Деплой (Cloud Shell):

```
gcloud config set project <PROJECT_ID>
bash deploy.sh        # вмикає api, створює firestore, бакет, сервісний акаунт, деплоїть
```

Скрипт наприкінці друкує адресу і API-ключ (заголовок `X-API-Key`). Перевірка:

```
curl -H "X-API-Key: $(cat .api_key)" -F file=@samples/door_valid.jpg <URL>/api/scan
```

Локально: `pip install -r requirements.txt pytest httpx && pytest`, Vision і Firestore в тестах підмінені.

У `samples/real` справжні фото з Wikimedia Commons, в назві файлу правильний номер.
Після захисту `bash cleanup.sh`.
