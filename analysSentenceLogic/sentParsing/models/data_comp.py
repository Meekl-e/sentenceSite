import re

with open("data.txt", "r", encoding="UTF-8") as f:
    with open("proverbs_and_sayings.txt", "w", encoding="UTF-8") as file_to:
        lines = f.readlines()
        data = []
        for line in lines:
            line = line.rstrip().lower()
            line = re.sub(r'[;-():.,?!*%$№+=]', "", line)
            if len(line) == 0:
                continue
            line = "".join(line.split()[1:]) + "\n"
            data.append(line)
        file_to.writelines(data)
