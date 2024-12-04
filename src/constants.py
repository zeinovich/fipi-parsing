# Кол-во страниц, с которых нужно спарсить данные
QUANTITY_PAGES = 161

# Общая url ссылка. После "=" подставляется номер конкретной страницы
URL_PAGES = "https://ege.fipi.ru/bank/questions.php?proj=AF0ED3F2557F8FFC4C06F80B6803FD26&page="

# Получение id. Найти можно по этим тегам + атрибутам:
NAME_FOR_ID = "span"
ATTRS_ID = "canselect"

# Получение 1 блока (условие + задание). Найти можно по этим тегам + атрибутам:
NAME_FOR_BLOCK = "div"
ATTRS_BLOCK = "qblock"

# Получение только условия. Найти можно по этим тегам + атрибутам:
NAME_FOR_CONDITION = "div"
ATTRS_CONDITION = "hint"