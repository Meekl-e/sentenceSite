from django.core.files.storage import FileSystemStorage
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def __get_words_width(start_idx, stop_idx, WIDTH_WORDS):
    return int(sum([i[0] for i in WIDTH_WORDS[start_idx:stop_idx]]))


def __calculate_width(image=Image(), ctx=Drawing(), text=None, width=int()):
    if text is None:
        text = list()
    lst_width = []

    l_txt = len(text)
    start_idx = 0
    prev_width = 0

    for i in range(l_txt):

        metrics = ctx.get_font_metrics(image, " ".join(text[start_idx:i + 1]), False)

        lst_width.append((int(metrics.text_width - prev_width), int(metrics.text_height)))

        if metrics.text_width > width:


            start_idx = i + 1
            prev_width = 0


        else:

            prev_width = metrics.text_width

    return lst_width


def __calculate_once_width(image=Image(), ctx=Drawing(), text=None):
    if text is None:
        text = list()
    lst_width = {}
    for w in text:
        metrics = ctx.get_font_metrics(image, w, False)
        lst_width[w] = int(metrics.text_width)

    return lst_width


def __calculate_height(image=Image(), ctx=Drawing(), mutable_message=str(), SEPARATOR="\n\n", ):
    lst_height = []
    splitted_msg = mutable_message.split(SEPARATOR)
    for idx in range(len(splitted_msg)):
        metrics = ctx.get_font_metrics(image, SEPARATOR + SEPARATOR.join(splitted_msg[:idx + 1]), True)
        lst_height.append(int(metrics.text_height))

    lst_height.append(int(ctx.get_font_metrics(image, SEPARATOR, True).text_height))

    return lst_height


def __split_lines(image=Image(), ctx=Drawing(), width=int(), WIDTH_WORDS=None, splt_text=None, SEPARATOR="\n\n"):
    """Разделяет текст на строки """

    if splt_text is None:
        splt_text = []
    if WIDTH_WORDS is None:
        WIDTH_WORDS = list()
    width_text = __get_words_width(0, -1, WIDTH_WORDS)

    message = ""

    if width_text > width:
        start_slice = 0

        for idx, word in enumerate(splt_text.copy()):
            w = __get_words_width(start_slice, idx + 1, WIDTH_WORDS)

            if w != 0 and w >= width:

                if idx - start_slice == 1:
                    width_word = WIDTH_WORDS[idx][0]
                    if width_word >= width:
                        width = width_word

                message += " ".join(splt_text[start_slice:idx]) + SEPARATOR

                start_slice = idx

        message += " ".join(splt_text[start_slice:])
    else:

        return " ".join(splt_text), width, WIDTH_WORDS[0][1]
    return message, width, int(ctx.get_font_metrics(image, message, True).text_height)


def __create_coordinates(WIDTH_WORDS, HEIGHT_LINES, mutable_message, adding, SEPARATOR="\n\n"):
    """Создает координаты для линий и связей"""

    coordinates = []

    full_idx = 0
    lst_split = mutable_message.split(SEPARATOR)

    for i, line in enumerate(lst_split):
        for idx, word in enumerate(line.split()):
            end_x, _ = WIDTH_WORDS[full_idx]

            all_y = HEIGHT_LINES[i]

            if idx != 0:
                start_x = __get_words_width(full_idx - idx, full_idx, WIDTH_WORDS)

            else:
                start_x = 0
            end_x += start_x

            coordinates.append((start_x + 5, end_x - 5, all_y))

            full_idx += 1

    return coordinates


def __draw_line(ctx, x_start, x_end, y, type="none", height=int()):
    """Подчеркивает слова
    Обозначения:
    ____ - line
    ==== - double_line
    _ _ _ - dotted_line
    _._._ - dotted_circle_line
    \/\/ - wavy_line
    O - circle
    """

    if type == "line":
        ctx.line((x_start, y), (x_end, y))
    elif type == "double_line":
        ctx.line((x_start, y), (x_end, y))
        ctx.line((x_start, y + 5), (x_end, y + 5))
    elif type == "dotted_line":
        for i in range(x_start, x_end, 10):
            ctx.line((i, y), (i + 5, y))
    elif type == "dotted_circle_line":

        for i in range(x_start, x_end, 12):
            ctx.line((i, y), (i + 6, y))

            ctx.circle((i + 9, y), (i + 9 + 1, y + 1))
    if type == "wavy_line":
        up, down = 180, 0
        f_s = ctx.fill_color
        f_sc = ctx.stroke_color
        ctx.fill_color = Color("White")
        ctx.stroke_color = Color("Black")
        for i in range(x_start + 12, x_end + 1, 12):
            ctx.ellipse((i, y + 2), (6, 2), (up, down))
            up, down = down, up
        ctx.fill_color = f_s
        ctx.stroke_color = f_sc
    if type == "circle":
        f_c = ctx.fill_color
        f_sc = ctx.stroke_color
        ctx.fill_color = Color("transparent")
        ctx.stroke_color = Color("Black")

        ctx.ellipse(((x_start + x_end) // 2, y - height // 2), ((x_start + x_end) // 2 + 2 - x_start, height))
        ctx.fill_color = f_c
        ctx.stroke_color = f_sc


def __draw_question(id_from, id_to, question, coordinates, height_letter, width_question, y_used, ctx=Drawing(),
                    width=0, ):
    """Coздает связи для слов """

    def __check_add_sep(y_question, y_line):

        if y_question - y_line <= 0:
            y_used["SEPS"] += 1
            return True
        return False

    def __draw_with_step(start, stop, step):
        stop -= step
        for i in range(start, stop, step):

            i = __check_spaces(0, width, i)

            if __check_add_sep(i, i - HEIGHT_LINE): return True
            ctx.line((width, i), (0, i))

    def __draw_arrow(x, y):

        if id_from > id_to:
            ctx.text(x, y, question)
        else:
            if (x - width_question < 0):
                ctx.text(0, y, question)
            else:
                ctx.text(x - width_question, y, question)
        y_cor = word_y2 + HEIGHT_LINE - height_letter + 5
        ctx.line((x, y), (x, y_cor))
        ctx.line((x, y_cor), (x + 7, y_cor - 7))
        ctx.line((x, y_cor), (x - 7, y_cor - 7))

    def __check_spaces(x1, x2, y):
        x1, x2 = sorted((x1, x2))

        def __check_min(x):
            if type(x) == type(str()):
                return float("inf")
            else:
                return abs(y - x)

        if y_used.get(y) is None:
            y = min(y_used.keys(), key=__check_min)



        #minus = sum([w for x1_check, x2_check, w in y_used[y] if x1_check<=x1<=x2_check or x1_check<=x2<=x2_check])
        minus = 0
        for x1_check, x2_check, w in y_used[y]:
            x1_check, x2_check = sorted((x1_check, x2_check))
            if  x1<=x1_check <= x2 or x1 <= x2_check <= x2:
                minus+=w

        y_used[y].append((x1, x2, 3))
        if id_from > id_to:
            y_used[y].append((x2 - 10, x2 + width_question+10, round(ctx.font_size *0.6)))
        else:
            y_used[y].append((x2 - 10, x2 - width_question+10, round(ctx.font_size *0.6)))

        y -= minus
        y -= height_letter + 2

        return y

    keys = list(y_used.keys())
    if len(keys) != 2:
        HEIGHT_LINE = abs(keys[1] - keys[0])
    else:
        HEIGHT_LINE = keys[0]

    start_x1, end_x1, y1 = coordinates[id_from]

    start_x2, end_x2, y2 = coordinates[id_to]

    word_y1 = y1 - HEIGHT_LINE
    word_y2 = y2 - HEIGHT_LINE

    x1 = (start_x1 + end_x1) // 2 + 5
    x2 = (start_x2 + end_x2) // 2 - 5

    if y1 == y2:

        y1 = __check_spaces(x1, x2, y1)

        if __check_add_sep(y1, word_y1): return True

        ctx.line((x1, word_y1 + HEIGHT_LINE - height_letter + 5), (x1, y1))
        ctx.line((x1, y1), (x2, y1))

        __draw_arrow(x2, y1)

    elif y1 < y2:
        y1 = __check_spaces(x1, width, y1)
        if __check_add_sep(y1, word_y1): return True

        ctx.line((x1, word_y1 + HEIGHT_LINE - height_letter + 5), (x1, y1))

        ctx.line((x1, y1), (width, y1))

        start_y = y1 + HEIGHT_LINE
        end_y = y2

        __draw_with_step(start_y, end_y, HEIGHT_LINE)

        y2 = __check_spaces(x2, 0, y2)

        if __check_add_sep(y2, word_y2): return True

        ctx.line((0, y2), (x2, y2))

        __draw_arrow(x2, y2)


    elif y1 > y2:
        y1 = __check_spaces(x1, 0, y1)
        if __check_add_sep(y1, word_y1): return True
        ctx.line((x1, y1), (x1, word_y1 + HEIGHT_LINE - height_letter + 5))

        ctx.line((0, y1), (x1, y1))

        start_y = y2 + HEIGHT_LINE
        end_y = y1

        __draw_with_step(start_y, end_y, HEIGHT_LINE)

        y2 = __check_spaces(x2, width, y2)
        if __check_add_sep(y2, word_y2): return True

        ctx.line((width, y2), (x2, y2))

        __draw_arrow(x2, y2)


def __create_text(image, ctx, width, WIDTH_WORDS, text, question_list, WIDTH_QUESTIONS, SEPARATOR):
    mutable_message, width, height = __split_lines(image, ctx, width, WIDTH_WORDS, text, SEPARATOR)

    HEIGHT_LINES = __calculate_height(image, ctx, mutable_message, SEPARATOR)

    ADDING = HEIGHT_LINES[-1]

    coordinates = __create_coordinates(WIDTH_WORDS, HEIGHT_LINES, mutable_message, ADDING, SEPARATOR)

    seps_cnt = len(SEPARATOR)

    y_used = dict({i: list() for i in HEIGHT_LINES})
    y_used["SEPS"] = seps_cnt

    for id_from, id_to, question in question_list:
        if __draw_question(id_from, id_to, question, coordinates, WIDTH_WORDS[0][1], WIDTH_QUESTIONS[question],
                           y_used, ctx, width): break

    if y_used["SEPS"] != seps_cnt:
        f_s = ctx.font_size
        f_c = ctx.fill_color
        f_f = ctx.font_family
        ctx.clear()
        ctx.fill_color = f_c
        ctx.font_family = f_f
        ctx.font_size = f_s
        return __create_text(image, ctx, width, WIDTH_WORDS, text, question_list, WIDTH_QUESTIONS,
                             "\n" * y_used["SEPS"])

    return coordinates, mutable_message, width, height, ADDING


def draw(sentence, lined, question_list, PARAM=None):
    """
    Возвращает url картинки в файл storage
    sentence - разбитый на токены текст
    len(sentence) = len(lined)
    """
    if PARAM is None:
        PARAM = getDefaultParametrs()
    if len(sentence) > len(lined):
        raise ValueError(f"Длина токенов {len(sentence)} != длине подчеркиваний {len(lined)}")
    # name = ""
    # for letter in PARAM["name"]:
    #     name += alphabet_dict.get(letter,"_")
    # PARAM["name"] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    if FileStorage.exists(f"images_sentences/{PARAM['name']}.png"):
        FileStorage.delete(f"images_sentences/{PARAM['name']}.png")

    with Image(width=PARAM["width"], height=1, background=Color("WHITE"), ) as img:
        with Drawing() as ctx:
            SEPARATOR = "\n\n"

            ctx.fill_color = PARAM["color"]
            ctx.font_family = PARAM["font"]
            ctx.font_size = PARAM["size"]

            WIDTH_WORDS = __calculate_width(img, ctx, sentence, PARAM["width"])
            WIDTH_QUESTIONS = __calculate_once_width(img, ctx, {i[2] for i in question_list})

            question_list.sort(key=lambda coords: abs(coords[0] - coords[1]))

            coordinates, mutable_message, width, height, ADDING = __create_text(img, ctx, PARAM["width"], WIDTH_WORDS, sentence,
                                                                                question_list, WIDTH_QUESTIONS,
                                                                                SEPARATOR)
            img.resize(width, height + ADDING)

            for idx, word in enumerate(sentence):
                type = lined[idx]
                start_x, end_x, y = coordinates[idx]
                __draw_line(ctx, start_x, end_x, y, type, WIDTH_WORDS[0][1])

            ctx.text(0, ADDING - 5, mutable_message)

            ctx.draw(img)

            file = open(f"media/images_sentences/{PARAM['name']}.png", "wb")
            img.format = "png"
            img.save(file=file)
            file.close()
            #file = open(f"media/images_sentences/{PARAM['name']}.png", "br")
            #name = FileStorage.save(PARAM["name"], file)
            #file.close()
            print("SAVE")
            return FileStorage.url(f"images_sentences/{PARAM['name']}.png")


def getDefaultParametrs():
    return {"color": Color('BLACK'), "font": "Georgia", "size": 25, "name": "image.png","width":500}


FileStorage = FileSystemStorage()

"""
sentence = open("text.txt", "r", encoding="UTF-8").read()
sentence = sentence.replace("\n", "")
count_words = len(sentence.split())
print(count_words)
cnt = []

PARAMS = {"color":Color('BLACK'), "font":"Georgia", "size":25, "name":"image.png" }
for width in range(10, 5001, 100):
    for size in range(1, 101, 10):
        PARAMS["size"] = size
        PARAMS["name"] = f"{width}_{size}.png"
        
seconds = datetime.datetime.now()
print(seconds)
lines = ["circle"] + ["wavy_line"] * count_words
question_list = [(30, 95, "какой?"), (12, 96, "кто?"), (97, 0, "почему?"), (3, 10, "почему?"), (11, 12, "почему?"),
                 (23, 56, "почему?"),
                 (95, 5, "почему?"), (8, 17, "почему?"), (10, 11, "почему?"), (67, 89, "почему?"),
                 (103, 110, "почему?")]
#question_list = [ (0, 110)]

draw(30000, 1,
     sentence, lines, question_list)
secodns_end = datetime.datetime.now()

t = secodns_end - seconds
cnt.append(t.microseconds + t.seconds * 1000000)
print("======================")
print("Время выполнения:", t.seconds // 60, "минут", t.seconds % 60, "секунд")
#print("Скорость", round(count_words / (t.seconds + 0.000000000000000000001), 3), "слов в секунду")
print("======")
s_cnt = sum(cnt)
l_cnt = len(cnt)
print("Всего:", round(s_cnt / 1000000, 3), "с", s_cnt, "микросекунд")
print("Среднее:", round((s_cnt / l_cnt) / 1000000, 3), "с", round(s_cnt / l_cnt, 3), "микросекунд")
"""
alphabet_dict = {
    'а': "01", 'б': "02", 'в': "03", 'г': "04", 'д': "05", 'е': "06", 'ё': "07", 'ж': "08", 'з': "09",
    'и': "10", 'й': "11", 'к': "12", 'л': "13", 'м': "14", 'н': "15", 'о': "16", 'п': "17",
    'р': "18", 'с': "19", 'т': "20", 'у': "21", 'ф': "22", 'х': "23", 'ц': "24", 'ч': "25",
    'ш': "26", 'щ': "27", 'ъ': "28", 'ы': "29", 'ь': "30", 'э': "31", 'ю': "32", 'я': "33",
    '.': "34", ',': "35", '!': "36", '?': "37", ':': "38", ';': "39", '—': "40", '-': "41",
    '(': "42", ')': "43", '"': "44", "'": "45", '{': "46", '}': "47", '<': "48", '>': "49",
    '/': "50", '\\': "51", '|': "52", '[': "53", ']': "54", '№': "55", '#': "56", '$': "57",
    '%': "58", '^': "59", '&': "60", '*': "61", '@': "62", '=': "63", '+': "64", '~': "65",
    '`': "66", '0': "67", '1': "68", '2': "69", '3': "70", '4': "71", '5': "72", '6': "73",
    '7': "74", '8': "75", '9': "76", " ": "-"
}
