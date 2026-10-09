# Справжні фото контейнерів

Фото з [Wikimedia Commons](https://commons.wikimedia.org) під вільними ліцензіями (CC BY-SA 3.0 / 4.0).
Ім'я файлу — правильний номер контейнера (ISO 6346), тож для кожного фото відома очікувана відповідь.
У частини фото обрізано підпис із номером, який був доданий автором унизу кадру, щоб OCR читав номер
лише з самого контейнера. Файли `*_door.jpg` — вирізані з тих самих фото ділянки з номером: так виглядає
знімок, який користувач робить телефоном зблизька.

## Результати на розгорнутому сервісі (Cloud Vision, `TEXT_DETECTION`), 2026-10-10

| Номер | Загальний план | Крупний план (`_door`) |
|---|---|---|
| `APZU3737897` | ❌ `APNU3737891` (invalid_check_digit) | ✅ `APZU3737897` |
| `APZU4203860` | ❌ not_found | ❌ not_found |
| `BMOU5962924` | ✅ `BMOU5962924` | — |
| `CAXU6627516` | ✅ `CAXU6627516` | — |
| `CBHU1715124` | ❌ not_found | ❌ not_found |
| `CKLU2038779` | ✅ `CKLU2038779` | — |
| `CMAU4307598` | ❌ `CHAU4307598` (invalid_check_digit) | ✅ `CMAU4307598` |
| `GESU2796740` | ❌ not_found | ✅ `GESU2796740` |
| `GLDU2976203` | ❌ `GLOU2976203` (invalid_check_digit) | ❌ `GLOU2976203` (invalid_check_digit) |
| `HLXU8359262` | ✅ `HLXU8359262` | — |
| `MSCU1175102` | ❌ not_found | ❌ not_found |
| `MSCU4863177` | ❌ `TTNU9098849` (invalid_check_digit) | ❌ `MSCU4863171` (invalid_check_digit) |
| `OOLU2891972` | ❌ `OILU1891172` (invalid_check_digit) | ❌ not_found |
| `TCLU4684070` | ❌ not_found | ❌ not_found |

Загальний план: **4 з 14**. Крупний план (лише для тих, що не впізнались на загальному): **3 з 10**.
Разом номер прочитано для **7 з 14** контейнерів.

Що видно з помилок:

- **Дрібний текст на загальних планах.** Фото зняті здалеку, в кадрі кілька контейнерів, номер займає
  кілька десятків пікселів. Vision або не бачить його, або читає сусідній контейнер. Крупний план лікує
  це (`APZU3737897`, `CMAU4307598`, `GESU2796740`).
- **Вертикальні написи** (`APZU4203860`, `TCLU4684070`, `MSCU1175102`): Vision читає їх посимвольно, а
  номер з них не складається. Відома межа PoC.
- **Схожі літери в коді власника.** `GLDU` прочитано як `GLOU`; виправлення зараз працює лише для пар
  цифра/літера (`0↔O`, `1↔I`, `5↔S`…), а не для `D↔O`, `M↔H`. Контрольна цифра таку помилку ловить
  (статус `invalid_check_digit`), але не виправляє.
- **Контрольна цифра в рамці** читається гірше за решту (`MSCU 486317 [7]` → `1`): рамка заважає OCR.
  Сервіс показує очікувану цифру в полі `expected_check_digit`.
- **Низька роздільність** (`CBHU1715124`, `OOLU2891972` з 1024-px оригіналів): після вирізання
  номер має висоту 10–15 px, цього замало.

## Атрибуція

| Файл | Джерело | Автор | Ліцензія |
|---|---|---|---|
| `APZU3737897.jpg` | [Container 【 22G1 】 APZU 373789(7) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_APZU_373789(7)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `APZU4203860.jpg` | [APL 42G1 APZU 420386 0.jpg](https://commons.wikimedia.org/wiki/File:APL_42G1_APZU_420386_0.jpg) | Col André Kritzinger | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| `BMOU5962924.jpg` | [Beacon 45G1 BMOU 596292 4.jpg](https://commons.wikimedia.org/wiki/File:Beacon_45G1_BMOU_596292_4.jpg) | Col André Kritzinger | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| `CAXU6627516.jpg` | [Container 【 22G1 】 CAXU 662751(6) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_CAXU_662751(6)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `CBHU1715124.jpg` | [Cosco 42G1 CBHU 171512 4.jpg](https://commons.wikimedia.org/wiki/File:Cosco_42G1_CBHU_171512_4.jpg) | Col André Kritzinger | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| `CKLU2038779.jpg` | [Container 【 22G1 】 CKLU 203877(9) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_CKLU_203877(9)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `CMAU4307598.jpg` | [CMA CGM 45G1 CMAU 430759 8.jpg](https://commons.wikimedia.org/wiki/File:CMA_CGM_45G1_CMAU_430759_8.jpg) | Col André Kritzinger | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| `GESU2796740.jpg` | [Container 【 22G1 】 GESU 279674(0) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_GESU_279674(0)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `GLDU2976203.jpg` | [Container 【 22G1 】 GLDU 297620(3) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_GLDU_297620(3)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `HLXU8359262.jpg` | [Container Hapag-Lloyd HLXU 835926 2, 1, Bad Wilhelmshöhe, Kassel.jpg](https://commons.wikimedia.org/wiki/File:Container_Hapag-Lloyd_HLXU_835926_2,_1,_Bad_Wilhelmsh%C3%B6he,_Kassel.jpg) | GeorgDerReisende | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `MSCU1175102.jpg` | [Container 【 22G1 】 MSCU 117510(2) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_MSCU_117510(2)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `MSCU4863177.jpg` | [Container 【 42G1 】 MSCU 486317(7) 【 Pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_42G1_%E3%80%91_MSCU_486317(7)_%E3%80%90_Pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `OOLU2891972.jpg` | [Container 【 22G1 】 OOLU 289197(2) 【 Container pictures taken in Japan 】.jpg](https://commons.wikimedia.org/wiki/File:Container_%E3%80%90_22G1_%E3%80%91_OOLU_289197(2)_%E3%80%90_Container_pictures_taken_in_Japan_%E3%80%91.jpg) | Gazouya-japan | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| `TCLU4684070.jpg` | [Container TRITON TCLU 468407 0, 1, Bad Wilhelmshöhe, Kassel.jpg](https://commons.wikimedia.org/wiki/File:Container_TRITON_TCLU_468407_0,_1,_Bad_Wilhelmsh%C3%B6he,_Kassel.jpg) | GeorgDerReisende | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |

Файли `*_door.jpg` — похідні (вирізки) з відповідних фото, та сама ліцензія і автор.
