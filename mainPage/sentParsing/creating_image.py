import random
from textwrap import wrap
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image
import datetime
import re


def __calculate_width(image=Image(), ctx=Drawing(), text=list()):
    lst_width = []
    for w in text + [" "]:
        metrics = ctx.get_font_metrics(image, w, False)
        lst_width.append((int(metrics.text_width), int(metrics.text_height)))

    return lst_width

def get_words_width(start_idx, stop_idx, WIDTH_WORDS):
    if stop_idx == -1:
        spaces = len(WIDTH_WORDS) - 1 - start_idx
    else:
        spaces = stop_idx - start_idx

    return int(sum([i[0]-1.3 for i in WIDTH_WORDS[start_idx:stop_idx]]) + WIDTH_WORDS[-1][0] * spaces)
def __split_lines(image=Image(), ctx=Drawing(), width=int(), WIDTH_WORDS=list(),text=""):
    """Разделяет текст на строки """
    SEPARATOR = "\n\n"






    width_text = get_words_width(0, -1,WIDTH_WORDS)

    message = ""
    splt_text = text.split()

    if width_text > width:
        start_slice = 0

        for idx, word in enumerate(splt_text.copy()):
            w = get_words_width(start_slice, idx + 1,WIDTH_WORDS)

            if w != 0 and w >= width:

                if idx - start_slice == 1:
                    width_word = WIDTH_WORDS[idx][0]
                    if width_word >= width:
                        width = width_word

                message += " ".join(splt_text[start_slice:idx]) + SEPARATOR

                start_slice = idx

        message += " ".join(splt_text[start_slice:])
    else:
        return text, width, WIDTH_WORDS[0][1]
    return message, width, int(ctx.get_font_metrics(image, message, True).text_height)


def __create_coordinates(image,ctx, WIDTH_WORDS,mutable_message, adding):
    """Создает координаты для линий"""

    def eval_metrics(txt):
        """Quick helper function to calculate width/height of text."""
        metrics = ctx.get_font_metrics(image, txt, True)
        return (int(metrics.text_width), int(metrics.text_height))

    coordinates = []
    SEPARATOR = "\n\n"

    full_idx  =0
    lst_split = mutable_message.split(SEPARATOR)
    for i, line in enumerate(lst_split):

        for idx, word in enumerate(line.split()):

            end_x, end_y = WIDTH_WORDS[full_idx]
            if i != 0:
                all_y = eval_metrics(SEPARATOR.join(lst_split[:i]))[1] + adding + end_y

            else:
                all_y = adding

            if idx != 0:
                start_x = get_words_width(full_idx-idx, full_idx, WIDTH_WORDS)

            else:
                start_x = -5
            end_x += start_x


            coordinates.append((start_x + 5, end_x, all_y))
            full_idx+=1


    return coordinates


def draw_line(ctx, x_start, x_end, y, type="none"):
    if type == "line":
        ctx.line((x_start, y), (x_end, y))
    if type == "double_line":
        ctx.line((x_start, y), (x_end, y))
        ctx.line((x_start, y + 5), (x_end, y + 5))
    if type == "dotted_line":

        for i in range(x_start, x_end, 20):
            ctx.line((i, y), (i + 10, y))
    if type == "dotted_circle_line":

        for i in range(x_start, x_end, 20):
            ctx.line((i, y), (i + 10, y))

            ctx.point(i + 15, y)


def draw(width, height, sentence, lined):
    with Image(width=width, height=height) as img:
        with Drawing() as ctx:
            ctx.fill_color = Color('WHITE')
            ctx.font_family = 'Times New Roman'
            ctx.font_size = 25
            ADDING = 50
            WIDTH_WORDS = __calculate_width(img, ctx, sentence.split())

            mutable_message, width, height = __split_lines(img, ctx, width,WIDTH_WORDS, sentence)

            coordinates = __create_coordinates(img, ctx,WIDTH_WORDS, mutable_message, ADDING)

            img.resize(width, height + ADDING)
            ctx.text(0, ADDING - 5, mutable_message)
            for idx, word in enumerate(sentence.split()):
                type = lined[idx]
                start_x, end_x, y = coordinates[idx]
                draw_line(ctx, start_x, end_x, y, type)
            ctx.draw(img)

            img.save(filename='image.png')


sentence = open("text.txt", "r", encoding="UTF-8").read()
sentence = sentence.replace("\n", "")
count_words = len(sentence.split())
print(count_words)
seconds = datetime.datetime.now()
print(seconds)
lines = ["double_line"]*count_words

draw(1000, 1000,
     sentence, lined=lines)
secodns_end = datetime.datetime.now()

t = secodns_end - seconds
print("======================")
print("Время выполнения:",t.seconds//60,"минут",t.seconds%60, "секунд" )
print("Скорость",round(count_words/t.seconds, 3), "слов в секунду")
