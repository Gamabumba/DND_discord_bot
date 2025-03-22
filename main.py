import discord
import random
import re
from discord.ext import commands

import settings
import crit_fail_message
import crit_succ_message
import jokes

logger = settings.logging.getLogger('bot')


def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='#', intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f'User: {bot.user}')
        await bot.tree.sync()

    @bot.hybrid_command(
        description='Типа описание',
        brief='Пингует бота',
    )
    async def ping(ctx):
        await ctx.send('По еблу себе попингуй')

    @bot.command()
    async def joined(ctx, who: discord.Member):
        await ctx.send(who.joined_at)

    @bot.command(
        brief='Бросок костей DnD'
    )
    async def joke(ctx):
        joke = jokes.get_random_joke()
        await ctx.send(joke)

    @bot.hybrid_command(
        brief='Бросок костей DnD'
    )
    async def roll(ctx, *, input_string: str):
        # Регулярное выражение для парсинга шаблонов <кол-во>d<грани> и +<кол-во>d<граней> или -<число>
        dice_pattern = re.compile(r'([+-]?)\s*(\d*)d(\d+)|([+-]?\d+)')

        rolls = []
        total_sum = 0
        crit_message = None
        detailed_rolls = []

        # Парсим выражение
        for match in dice_pattern.finditer(input_string):
            if match.group(2) and match.group(3):  # Это часть типа '2d6' или '-2d6'
                sign = match.group(1) if match.group(1) else '+'
                count = int(match.group(2)) if match.group(2) else 1
                sides = int(match.group(3))

                roll_results = []
                for _ in range(abs(count)):
                    roll = random.randint(1, sides)
                    roll_results.append(roll)

                    # Проверка на критический промах или успех при 1d20
                    if abs(count) == 1 and sides == 20:
                        if roll == 1:
                            crit_message = crit_fail_message.get_random_crit_message()
                        elif roll == 20:
                            crit_message = crit_succ_message.get_random_crit_message()

                roll_with_sign = f'{sign}{count}d{sides} ({", ".join(map(str, roll_results))})'
                detailed_rolls.append(roll_with_sign)
                rolls.append(sum(roll_results) * (1 if sign == '+' else -1))

            elif match.group(4):  # Это статичное число
                static_number = int(match.group(4))
                sign = '+' if static_number >= 0 else '-'
                detailed_rolls.append(f'{sign}{abs(static_number)}')
                rolls.append(static_number)

        total_sum = sum(rolls)

        # Формируем ответ
        rolls_display = " ".join(detailed_rolls)
        result_message = f"Результат: {rolls_display}\nИтого: {total_sum}"

        if crit_message:
            result_message += f"\n{crit_message}"

        await ctx.send(result_message)

    @bot.command(
        brief='Показывает все хоумбрю из файла homebrew.txt'
    )
    async def homebrew(ctx):
        try:
            with open('homebrew.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                if not content.strip():
                    await ctx.send("Файл homebrew.txt пуст.")
                else:
                    await ctx.send(content)
        except FileNotFoundError:
            await ctx.send("Файл homebrew.txt не найден.")
        except Exception as e:
            await ctx.send(f"Произошла ошибка при чтении файла homebrew.txt: {e}")

    @bot.command(
        brief='Добавляет новое правило в файл homebrew.txt'
    )
    async def addhomebrew(ctx, *, rule: str):
        try:
            # Читаем текущие правила из файла
            try:
                with open('homebrew.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
            except FileNotFoundError:
                lines = []

            # Определяем номер нового правила
            if lines:
                last_line = lines[-1].strip()
                if last_line:
                    last_number = int(last_line.split('. ')[0])
                else:
                    last_number = 0
            else:
                last_number = 0

            new_number = last_number + 1
            new_rule = f"{new_number}. {rule}\n"

            # Записываем новое правило в файл
            with open('homebrew.txt', 'a', encoding='utf-8') as file:
                file.write(new_rule)

            await ctx.send(f"Правило #{new_number} добавлено успешно.")
        except Exception as e:
            await ctx.send(f"Произошла ошибка при добавлении правила в файл homebrew.txt: {e}")

    bot.run(settings.DISCORD_API, root_logger=True)


if __name__ == '__main__':
    run()