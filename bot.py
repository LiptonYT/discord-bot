import os
import discord
from discord.ext import commands
from datetime import datetime, timezone


# =========================================================
# НАСТРОЙКИ
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

# Канал, куда приходят заявки
MODERATION_CHANNEL_ID = 1533076060386623508

# Канал кадрового аудита
AUDIT_CHANNEL_ID = 1533076137209495642

# Роль модератора
MODERATOR_ROLE_ID = 1533075692785504327


# =========================================================
# РОЛИ ДЛЯ КАЖДОГО ЗВАНИЯ
# =========================================================
#
# ВАЖНО:
# В каждый список вписывай ID ролей, которые должны
# выдаваться именно при выборе этого звания.
#
# Можно указать несколько ролей.
#

RANK_ROLES = {

    "Рядовой": [
        1533075782790807682,
        1533075727241576619,
        1533075731054071959,
        1533075743347572786,
        1533075745751175299,
        1533075784858865704,
        1533075786175746108,
        1533075845663690842,
    ],

    "Младший сержант": [
        1533075781629251735,
        1533075725983285298,
        1533075731054071959,
        1533075743347572786,
        1533075745751175299,
        1533075784858865704,
        1533075786175746108,
        1533075845663690842,
    ],

    "Сержант": [
        1554097028357955615,
        1533075825510060132,
    ],

    "Старший сержант": [
        1533075778399637674,
        1533075825510060132,
    ],

    "Старшина": [
       1533075777179095212,
       1533075825510060132,
    ],

    "Прапорщик": [
        1533075775777931385,
        1533075825510060132,
    ],

    "Ст прапорщик": [
       1533075774134026350,
       1533075825510060132,
    ],

    "Младший лейтенант": [
        1533075772950974474,
        1533075825510060132,
    ],

    "Лейтенант": [
        1533075771801866421,
        1533075825510060132,
    ],

    "Старший лейтенант": [
        1533075769881002036,
        1533075825510060132,
    ],

    "Капитан": [
        1533075768760991934,
        1533075825510060132,
    ],

    "Майор": [
        1533075759583723681,
        1533075825510060132,
    ],

    "Подполковник": [
        1533075757608337538,
        1533075825510060132,
    ],

    "Полковник": [
        1533075756031279318,
        1533075825510060132,
    ],
}


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# ВРЕМЕННЫЕ ЗАЯВКИ
# =========================================================

pending_applications = {}


# =========================================================
# ПРОВЕРКА МОДЕРАТОРА
# =========================================================

def is_moderator(member: discord.Member) -> bool:

    return any(
        role.id == MODERATOR_ROLE_ID
        for role in member.roles
    )


# =========================================================
# ПОЛУЧЕНИЕ РОЛЕЙ ЗВАНИЯ
# =========================================================

def get_rank_roles(
    guild: discord.Guild,
    rank: str
):

    role_ids = RANK_ROLES.get(rank, [])

    roles = []

    for role_id in role_ids:

        role = guild.get_role(role_id)

        if role is not None:
            roles.append(role)

    return roles


# =========================================================
# КАДРОВЫЙ АУДИТ
# =========================================================

async def send_audit(
    guild: discord.Guild,
    title: str,
    color: discord.Color,
    fields: list,
    screenshot_url: str = None
):

    channel = guild.get_channel(
        AUDIT_CHANNEL_ID
    )

    if channel is None:

        print(
            "❌ Канал кадрового аудита не найден."
        )

        return False

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    for name, value, inline in fields:

        embed.add_field(
            name=name,
            value=value,
            inline=inline
        )

    if screenshot_url:

        embed.set_image(
            url=screenshot_url
        )

    embed.set_footer(
        text="Lipton | ГИБДД • Кадровый аудит"
    )

    try:

        await channel.send(
            embed=embed
        )

        print(
            "✅ Запись отправлена в кадровый аудит."
        )

        return True

    except discord.Forbidden:

        print(
            "❌ У бота нет прав писать "
            "в кадровый аудит."
        )

        return False

    except discord.HTTPException as error:

        print(
            f"❌ Ошибка отправки аудита: {error}"
        )

        return False


# =========================================================
# ВЫБОР ЗВАНИЯ
# =========================================================

class RankSelect(discord.ui.Select):

    def __init__(self):

        options = []

        for rank in RANK_ROLES:

            options.append(
                discord.SelectOption(
                    label=rank,
                    value=rank,
                    description=(
                        f"Претендовать на звание «{rank}»"
                    )[:100]
                )
            )

        super().__init__(
            placeholder="Выберите звание...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return

        rank = self.values[0]

        # Сохраняем выбранное звание
        pending_applications[
            interaction.user.id
        ] = {
            "guild_id": interaction.guild.id,
            "rank": rank
        }

        await interaction.response.send_modal(
            ApplicationModal(rank)
        )


# =========================================================
# VIEW ВЫБОРА ЗВАНИЯ
# =========================================================

class RankSelectView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            RankSelect()
        )


# =========================================================
# ФОРМА НОМЕРА УДОСТОВЕРЕНИЯ
# =========================================================

class ApplicationModal(discord.ui.Modal):

    def __init__(self, rank):

        super().__init__(
            title="Заявка в ГИБДД"
        )

        self.rank = rank

        self.badge_number = discord.ui.TextInput(
            label="Номер удостоверения",
            placeholder="Введите номер удостоверения",
            min_length=1,
            max_length=50,
            required=True
        )

        self.add_item(
            self.badge_number
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        application = pending_applications.get(
            interaction.user.id
        )

        if application is None:

            await interaction.response.send_message(
                "❌ Заявка потеряна. "
                "Начните оформление заново.",
                ephemeral=True
            )

            return

        application["badge_number"] = (
            self.badge_number.value
        )

        await interaction.response.send_message(
            "✅ Номер удостоверения сохранён.\n\n"
            f"🎖 Звание: **{self.rank}**\n"
            f"🪪 Номер: `{self.badge_number.value}`\n\n"
            "📷 Теперь отправьте **скриншот удостоверения** "
            "сообщением.",
            ephemeral=True
        )


# =========================================================
# КНОПКА ЗАПРОСИТЬ РОЛЬ
# =========================================================

class RequestRoleButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Запросить роль",
            emoji="📝",
            style=discord.ButtonStyle.primary,
            custom_id="request_role"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Эта кнопка работает "
                "только на сервере.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "🎖 **На какое звание вы претендуете?**",
            view=RankSelectView(),
            ephemeral=True
        )


# =========================================================
# ОСНОВНАЯ ПАНЕЛЬ
# =========================================================

class RoleRequestView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            RequestRoleButton()
        )


# =========================================================
# ПРИЁМ СКРИНШОТА
# =========================================================

@bot.event
async def on_message(
    message: discord.Message
):

    if message.author.bot:
        return

    user_id = message.author.id

    if user_id in pending_applications:

        application = pending_applications[
            user_id
        ]

        # -----------------------------------------------------
        # ПРОВЕРКА НОМЕРА
        # -----------------------------------------------------

        if "badge_number" not in application:

            await message.reply(
                "❌ Сначала заполните номер "
                "удостоверения."
            )

            return

        # -----------------------------------------------------
        # ПРОВЕРКА СКРИНШОТА
        # -----------------------------------------------------

        if not message.attachments:

            await message.reply(
                "❌ Отправьте скриншот удостоверения."
            )

            return

        attachment = message.attachments[0]

        content_type = (
            attachment.content_type or ""
        )

        if not content_type.startswith("image/"):

            await message.reply(
                "❌ Необходимо отправить "
                "изображение."
            )

            return

        guild = message.guild

        if guild is None:
            return

        rank = application["rank"]

        # -----------------------------------------------------
        # ПОЛУЧАЕМ РОЛИ ЭТОГО ЗВАНИЯ
        # -----------------------------------------------------

        rank_roles = get_rank_roles(
            guild,
            rank
        )

        if not rank_roles:

            await message.reply(
                "❌ Для этого звания не найдены роли.\n\n"
                f"Звание: **{rank}**\n"
                "Проверь ID в `RANK_ROLES`."
            )

            return

        # -----------------------------------------------------
        # КАНАЛ МОДЕРАЦИИ
        # -----------------------------------------------------

        moderation_channel = guild.get_channel(
            MODERATION_CHANNEL_ID
        )

        if moderation_channel is None:

            await message.reply(
                "❌ Канал заявок не найден.\n"
                "Проверь `MODERATION_CHANNEL_ID`."
            )

            return

        screenshot_url = attachment.url

        # -----------------------------------------------------
        # СПИСОК РОЛЕЙ
        # -----------------------------------------------------

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in rank_roles
        )

        # -----------------------------------------------------
        # EMBED
        # -----------------------------------------------------

        embed = discord.Embed(
            title="📝 НОВАЯ ЗАЯВКА В ГИБДД",
            description=(
                "Проверьте данные кандидата.\n\n"
                "После проверки нажмите "
                "**Принять** или **Отклонить**."
            ),
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="👤 Кандидат",
            value=(
                f"{message.author.mention}\n"
                f"`{message.author.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎖 Звание",
            value=f"**{rank}**",
            inline=True
        )

        embed.add_field(
            name="🪪 Номер удостоверения",
            value=(
                f"`{application['badge_number']}`"
            ),
            inline=True
        )

        embed.add_field(
            name="🎭 Роли для выдачи",
            value=roles_text,
            inline=False
        )

        embed.set_image(
            url=screenshot_url
        )

        embed.set_footer(
            text="Lipton | ГИБДД • Кадровая заявка"
        )

        # -----------------------------------------------------
        # ОТПРАВЛЯЕМ МОДЕРАТОРУ
        # -----------------------------------------------------

        try:

            await moderation_channel.send(
                embed=embed,
                view=ModerationView(
                    user_id=message.author.id,
                    badge_number=application[
                        "badge_number"
                    ],
                    rank=rank,
                    role_ids=[
                        role.id
                        for role in rank_roles
                    ],
                    screenshot_url=screenshot_url
                )
            )

        except discord.Forbidden:

            await message.reply(
                "❌ Бот не может отправить "
                "заявку в канал модерации."
            )

            return

        # -----------------------------------------------------
        # УДАЛЯЕМ ВРЕМЕННЫЕ ДАННЫЕ
        # -----------------------------------------------------

        pending_applications.pop(
            user_id,
            None
        )

        await message.reply(
            "✅ **Заявка отправлена!**\n\n"
            f"🎖 Звание: **{rank}**\n"
            f"🪪 Удостоверение: "
            f"`{application['badge_number']}`\n\n"
            "📋 Заявка передана модераторам."
        )

    await bot.process_commands(message)


# =========================================================
# КНОПКА ПРИНЯТЬ
# =========================================================

class ApproveButton(discord.ui.Button):

    def __init__(
        self,
        user_id: int,
        badge_number: str,
        rank: str,
        role_ids: list,
        screenshot_url: str
    ):

        self.user_id = user_id
        self.badge_number = badge_number
        self.rank = rank
        self.role_ids = role_ids
        self.screenshot_url = screenshot_url

        super().__init__(
            label="Принять",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id=(
                f"approve:{user_id}:{rank}"
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return

        # -----------------------------------------------------
        # ПРОВЕРКА МОДЕРАТОРА
        # -----------------------------------------------------

        if not is_moderator(
            interaction.user
        ):

            await interaction.response.send_message(
                "❌ У тебя нет прав "
                "для обработки заявок.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        if guild is None:
            return

        # -----------------------------------------------------
        # ПОЛЬЗОВАТЕЛЬ
        # -----------------------------------------------------

        member = guild.get_member(
            self.user_id
        )

        if member is None:

            await interaction.response.send_message(
                "❌ Пользователь не найден "
                "на сервере.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # РОЛЬ БОТА
        # -----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ Не удалось определить "
                "роль бота.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ПОЛУЧАЕМ РОЛИ
        # -----------------------------------------------------

        roles_to_give = []

        missing_roles = []

        for role_id in self.role_ids:

            role = guild.get_role(
                role_id
            )

            if role is None:

                missing_roles.append(
                    role_id
                )

                continue

            roles_to_give.append(
                role
            )

        if not roles_to_give:

            await interaction.response.send_message(
                "❌ Роли этого звания не найдены.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ПРОВЕРКА ИЕРАРХИИ
        # -----------------------------------------------------

        for role in roles_to_give:

            if role >= bot_member.top_role:

                await interaction.response.send_message(
                    f"❌ Бот не может выдать роль "
                    f"**{role.name}**.\n\n"
                    "Перемести роль бота выше "
                    "этой роли.",
                    ephemeral=True
                )

                return

        # -----------------------------------------------------
        # ВЫДАЧА РОЛЕЙ
        # -----------------------------------------------------

        try:

            for role in roles_to_give:

                if role not in member.roles:

                    await member.add_roles(
                        role,
                        reason=(
                            f"Заявка ГИБДД одобрена. "
                            f"Звание: {self.rank}"
                        )
                    )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Discord запретил выдачу роли.\n\n"
                "Проверь право **Управление ролями** "
                "и положение ролей бота.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                f"❌ Ошибка Discord:\n`{error}`",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ТЕКСТ ВЫДАННЫХ РОЛЕЙ
        # -----------------------------------------------------

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in roles_to_give
        )

        # -----------------------------------------------------
        # КАДРОВЫЙ АУДИТ
        # -----------------------------------------------------

        await send_audit(
            guild,
            "🟢 КАДРОВЫЙ АУДИТ — ПРИНЯТ",
            discord.Color.green(),
            [
                (
                    "👤 Сотрудник",
                    (
                        f"{member.mention}\n"
                        f"`{member.id}`"
                    ),
                    False
                ),
                (
                    "🪪 Номер удостоверения",
                    f"`{self.badge_number}`",
                    True
                ),
                (
                    "🎖 Звание",
                    f"**{self.rank}**",
                    True
                ),
                (
                    "🎭 Выданные роли",
                    roles_text,
                    False
                ),
                (
                    "👮 Модератор",
                    interaction.user.mention,
                    False
                ),
                (
                    "📊 Статус",
                    "🟢 **ПРИНЯТ**",
                    False
                )
            ],
            self.screenshot_url
        )

        # -----------------------------------------------------
        # ОБНОВЛЯЕМ ЗАЯВКУ
        # -----------------------------------------------------

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.green()

        embed.add_field(
            name="📊 Результат",
            value=(
                "🟢 **ПРИНЯТ**\n"
                f"Модератор: "
                f"{interaction.user.mention}"
            ),
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        await interaction.response.send_message(
            "✅ **Заявка принята!**\n\n"
            f"👤 {member.mention}\n"
            f"🎖 Звание: **{self.rank}**\n\n"
            "🎭 Выданы роли:\n"
            f"{roles_text}\n\n"
            "📋 Запись отправлена "
            "в кадровый аудит.",
            ephemeral=True
        )


# =========================================================
# КНОПКА ОТКЛОНИТЬ
# =========================================================

class RejectButton(discord.ui.Button):

    def __init__(
        self,
        user_id: int,
        badge_number: str,
        rank: str,
        role_ids: list,
        screenshot_url: str
    ):

        self.user_id = user_id
        self.badge_number = badge_number
        self.rank = rank
        self.role_ids = role_ids
        self.screenshot_url = screenshot_url

        super().__init__(
            label="Отклонить",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id=(
                f"reject:{user_id}:{rank}"
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return

        # -----------------------------------------------------
        # ПРОВЕРКА МОДЕРАТОРА
        # -----------------------------------------------------

        if not is_moderator(
            interaction.user
        ):

            await interaction.response.send_message(
                "❌ У тебя нет прав "
                "для обработки заявок.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        if guild is None:
            return

        member = guild.get_member(
            self.user_id
        )

        if member is not None:

            member_text = (
                f"{member.mention}\n"
                f"`{member.id}`"
            )

        else:

            member_text = (
                f"`{self.user_id}`"
            )

        # -----------------------------------------------------
        # КАДРОВЫЙ АУДИТ
        # -----------------------------------------------------

        await send_audit(
            guild,
            "🔴 КАДРОВЫЙ АУДИТ — ОТКЛОНЁН",
            discord.Color.red(),
            [
                (
                    "👤 Кандидат",
                    member_text,
                    False
                ),
                (
                    "🪪 Номер удостоверения",
                    f"`{self.badge_number}`",
                    True
                ),
                (
                    "🎖 Запрашиваемое звание",
                    f"**{self.rank}**",
                    True
                ),
                (
                    "🎭 Роли звания",
                    "\n".join(
                        f"• <@&{role_id}>"
                        for role_id in self.role_ids
                    ),
                    False
                ),
                (
                    "👮 Модератор",
                    interaction.user.mention,
                    False
                ),
                (
                    "📊 Статус",
                    "🔴 **ОТКЛОНЁН**",
                    False
                )
            ],
            self.screenshot_url
        )

        # -----------------------------------------------------
        # ОБНОВЛЯЕМ ЗАЯВКУ
        # -----------------------------------------------------

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.red()

        embed.add_field(
            name="📊 Результат",
            value=(
                "🔴 **ОТКЛОНЁН**\n"
                f"Модератор: "
                f"{interaction.user.mention}"
            ),
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        await interaction.response.send_message(
            "❌ **Заявка отклонена.**\n\n"
            "📋 Запись отправлена "
            "в кадровый аудит.",
            ephemeral=True
        )


# =========================================================
# VIEW МОДЕРАЦИИ
# =========================================================

class ModerationView(discord.ui.View):

    def __init__(
        self,
        user_id: int,
        badge_number: str,
        rank: str,
        role_ids: list,
        screenshot_url: str
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            ApproveButton(
                user_id,
                badge_number,
                rank,
                role_ids,
                screenshot_url
            )
        )

        self.add_item(
            RejectButton(
                user_id,
                badge_number,
                rank,
                role_ids,
                screenshot_url
            )
        )


# =========================================================
# КОМАНДА /SETUP_ROLES
# =========================================================

@bot.tree.command(
    name="setup_roles",
    description="Создать панель запроса роли ГИБДД"
)
async def setup_roles(
    interaction: discord.Interaction
):

    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return

    if not is_moderator(
        interaction.user
    ):

        await interaction.response.send_message(
            "❌ У тебя нет прав для этой команды.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title="🟡 Lipton | ГИБДД",
        description=(
            "## 🎖 Запрос роли\n\n"
            "Нажмите **📝 Запросить роль**, "
            "чтобы оформить кадровую заявку.\n\n"
            "**Для оформления потребуется:**\n"
            "🎖 Выбрать звание\n"
            "🪪 Указать номер удостоверения\n"
            "📷 Отправить скриншот удостоверения\n\n"
            "После проверки модератором "
            "будут выданы роли, настроенные "
            "для выбранного звания."
        ),
        color=discord.Color.gold()
    )

    embed.set_footer(
        text="Lipton | ГИБДД • Кадровая система"
    )

    await interaction.channel.send(
        embed=embed,
        view=RoleRequestView()
    )

    await interaction.response.send_message(
        "✅ Панель запроса роли создана.",
        ephemeral=True
    )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    if not getattr(
        bot,
        "_views_added",
        False
    ):

        bot.add_view(
            RoleRequestView()
        )

        bot._views_added = True

    try:

        synced = await bot.tree.sync()

        print(
            f"✅ Бот запущен: {bot.user}"
        )

        print(
            f"✅ Slash-команд синхронизировано: "
            f"{len(synced)}"
        )

    except Exception as error:

        print(
            f"❌ Ошибка синхронизации: {error}"
        )


# =========================================================
# ПРОВЕРКА ТОКЕНА
# =========================================================

if not TOKEN:

    raise RuntimeError(
        "❌ DISCORD_TOKEN не найден.\n"
        "Задай переменную окружения DISCORD_TOKEN."
    )


# =========================================================
# ЗАПУСК
# =========================================================

bot.run(TOKEN)