import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN не найден в переменных окружения.")
    
GUILD_ID = 1533075462383730838

MODERATION_CHANNEL_ID = 1533076060386623508
AUDIT_CHANNEL_ID = 1533076137209495642

MODERATOR_ROLE_ID = 1533075692785504327


# =========================================================
# РОЛИ ДЛЯ КАЖДОГО ЗВАНИЯ
# =========================================================

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
        1533075702432403456,
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
        1533075702432403456,
    ],

    "Сержант": [
        1533075780312236082,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075739631550494,
        1533075722330046484,
        1533075702432403456,
    ],

    "Старший сержант": [
        1533075778399637674,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075739631550494,
        1533075722330046484,
        1533075702432403456,
    ],

    "Старшина": [
        1533075777179095212,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075702432403456,
    ],

    "Прапорщик": [
        1533075775777931385,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075702432403456,
    ],

    "Ст прапорщик": [
        1533075774134026350,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075702432403456,
    ],

    "Младший лейтенант": [
        1533075772950974474,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075702432403456,
    ],

    "Лейтенант": [
        1533075771801866421,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075702432403456,
        1533075739631550494,
    ],

    "Старший лейтенант": [
        1533075769881002036,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075731054071959,
        1533075702432403456,
    ],

    "Капитан": [
        1533075768760991934,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075739631550494,
        1533075731054071959,
        1533075702432403456,
    ],

    "Майор": [
        1533075759583723681,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075739631550494,
        1533075692785504327,
        1533075702432403456,
    ],

    "Подполковник": [
        1533075757608337538,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075739631550494,
        1533075692785504327,
        1533075695318732941,
        1533075702432403456,
    ],

    "Полковник": [
        1533075756031279318,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075739631550494,
        1533075692785504327,
        1533075695318732941,
        1533075702432403456,
    ],

    "Генерал-майор полиции": [
        1533075648577540238,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075692785504327,
        1533075695318732941,
        1533075754898690171,
        1533075650112655370,
        1533075664494657739,
        1533075653887525046,
        1533075732152975431,
    ],

    "Генерал-лейтенант полиции": [
        1533075752512258099,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075692785504327,
        1533075695318732941,
        1533075650112655370,
        1533075664494657739,
        1533075653887525046,
        1533075732152975431,
    ],

    "Генерал-полковник полиции": [
        1533075750301732864,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075692785504327,
        1533075695318732941,
        1533075664494657739,
        1533075653887525046,
        1533075732152975431,
    ],

    "Генерал полиции Российской Федерации": [
        1533075748292661380,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075692785504327,
        1533075695318732941,
        1533075750301732864,
        1533075664494657739,
        1533075653887525046,
        1533075732152975431,
    ],
}


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

def is_moderator(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True

    return any(
        role.id == MODERATOR_ROLE_ID
        for role in member.roles
    )


def find_rank(input_rank: str) -> str | None:
    """Вспомогательный поиск звания с игнорированием регистра"""
    clean_input = input_rank.strip().lower()
    for rank in RANK_ROLES:
        if rank.lower() == clean_input:
            return rank
    return None


def get_rank_roles(
    guild: discord.Guild,
    rank: str
) -> list[discord.Role]:

    roles = []

    for role_id in RANK_ROLES.get(rank, []):
        role = guild.get_role(int(role_id))

        if role is not None:
            roles.append(role)

    return roles


def get_embed_field(
    embed: discord.Embed,
    field_name: str
) -> str | None:

    for field in embed.fields:
        if field.name == field_name:
            return field.value

    return None


def parse_user_id(
    value: str | None
) -> int | None:

    if not value:
        return None

    match = re.search(
        r"`(\d{15,25})`",
        value
    )

    if match:
        return int(match.group(1))

    match = re.search(
        r"(\d{15,25})",
        value
    )

    if match:
        return int(match.group(1))

    return None


def get_rank_from_embed(
    embed: discord.Embed
) -> str | None:

    value = get_embed_field(
        embed,
        "🎖️ Звание"
    )

    if not value:
        return None

    clean = value.replace(
        "**",
        ""
    ).strip()

    if clean in RANK_ROLES:
        return clean

    for rank in RANK_ROLES:
        if rank in clean:
            return rank

    return None


# =========================================================
# КАДРОВЫЙ АУДИТ
# =========================================================

async def send_audit(
    guild: discord.Guild,
    title: str,
    color: discord.Color,
    fields: list[tuple[str, str, bool]]
) -> bool:

    channel = guild.get_channel(
        AUDIT_CHANNEL_ID
    )

    if channel is None:

        try:
            channel = await guild.fetch_channel(
                AUDIT_CHANNEL_ID
            )

        except Exception as error:

            print(
                f"❌ Канал аудита не найден: {error}"
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

    embed.set_footer(
        text="Lipton | ГИБДД • Кадровый аудит"
    )

    try:

        await channel.send(
            embed=embed
        )

        return True

    except Exception as error:

        print(
            f"❌ Ошибка отправки аудита: {error}"
        )

        return False


# =========================================================
# POPUP — ЗАЯВКА В ГИБДД
# =========================================================

class ApplicationModal(
    discord.ui.Modal
):

    def __init__(self):

        super().__init__(
            title="📝 Заявка в ГИБДД",
            timeout=300
        )

        # -----------------------------------------------------
        # ПОЛЯ ВВОДА (Modal поддерживает только TextInput)
        # -----------------------------------------------------

        self.rank_input = discord.ui.TextInput(
            label="🎖️ Звание",
            placeholder="Пример: Лейтенант, Майор, Сержант...",
            min_length=2,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )

        self.badge_number = discord.ui.TextInput(
            label="🪪 Номер удостоверения",
            placeholder="Введите номер служебного удостоверения",
            min_length=1,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )

        self.proof = discord.ui.TextInput(
            label="📎 Док-ва, что вы сотрудник ГИБДД",
            placeholder="Ссылка или номер удостоверения",
            min_length=1,
            max_length=500,
            required=True,
            style=discord.TextStyle.paragraph
        )

        self.add_item(self.rank_input)
        self.add_item(self.badge_number)
        self.add_item(self.proof)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Заявку можно подать только на сервере.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ПОЛУЧАЕМ И ПРОВЕРЯЕМ ДАННЫЕ
        # -----------------------------------------------------

        raw_rank = str(self.rank_input.value).strip()
        rank = find_rank(raw_rank)

        badge_number = str(
            self.badge_number.value
        ).strip()

        proof = str(
            self.proof.value
        ).strip()

        if not rank:

            available_ranks = ", ".join(list(RANK_ROLES.keys())[:5]) + "..."
            await interaction.response.send_message(
                f"❌ Неизвестное звание «**{raw_rank}**».\n"
                f"Убедитесь, что ввели звание корректно.\n"
                f"Доступные примеры: {available_ranks}",
                ephemeral=True
            )

            return

        if not badge_number:

            await interaction.response.send_message(
                "❌ Номер удостоверения обязателен.",
                ephemeral=True
            )

            return

        if not proof:

            await interaction.response.send_message(
                "❌ Укажите ссылку или номер удостоверения.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # РОЛИ
        # -----------------------------------------------------

        rank_roles = get_rank_roles(
            guild,
            rank
        )

        if not rank_roles:

            await interaction.response.send_message(
                f"❌ Для звания **{rank}** роли не найдены.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # КАНАЛ МОДЕРАЦИИ
        # -----------------------------------------------------

        moderation_channel = guild.get_channel(
            MODERATION_CHANNEL_ID
        )

        if moderation_channel is None:

            try:

                moderation_channel = await guild.fetch_channel(
                    MODERATION_CHANNEL_ID
                )

            except Exception:

                moderation_channel = None

        if moderation_channel is None:

            await interaction.response.send_message(
                "❌ Канал заявок не найден.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ПРОВЕРКА ИЕРАРХИИ
        # -----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ Не удалось определить бота.",
                ephemeral=True
            )

            return

        impossible_roles = [
            role
            for role in rank_roles
            if role >= bot_member.top_role
        ]

        if impossible_roles:

            await interaction.response.send_message(
                "❌ Бот не может выдать следующие роли:\n\n"
                + "\n".join(
                    f"• **{role.name}**"
                    for role in impossible_roles
                )
                + "\n\n"
                "Подними роль бота выше ролей ГИБДД.",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ТЕКСТ РОЛЕЙ
        # -----------------------------------------------------

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in rank_roles
        )

        # -----------------------------------------------------
        # EMBED ЗАЯВКИ
        # -----------------------------------------------------

        embed = discord.Embed(
            title="📝 НОВАЯ ЗАЯВКА В ГИБДД",
            description=(
                "Поступила новая заявка на получение роли.\n\n"
                "Проверьте данные кандидата и примите "
                "или отклоните заявку."
            ),
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="👤 Кандидат",
            value=(
                f"{interaction.user.mention}\n"
                f"`{interaction.user.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎖️ Звание",
            value=f"**{rank}**",
            inline=True
        )

        embed.add_field(
            name="🪪 Номер удостоверения",
            value=f"`{badge_number}`",
            inline=True
        )

        embed.add_field(
            name="📎 Док-ва, что вы сотрудник ГИБДД",
            value=proof[:1024],
            inline=False
        )

        embed.add_field(
            name="🎭 Роли для выдачи",
            value=roles_text[:1024],
            inline=False
        )

        embed.set_footer(
            text="Lipton | ГИБДД • Кадровая заявка"
        )

        # -----------------------------------------------------
        # ОТПРАВКА МОДЕРАТОРАМ
        # -----------------------------------------------------

        try:

            await moderation_channel.send(
                embed=embed,
                view=ModerationView()
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Бот не может отправить заявку.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                f"❌ Ошибка Discord: `{error}`",
                ephemeral=True
            )

            return

        # -----------------------------------------------------
        # ПРИВАТНОЕ ПОДТВЕРЖДЕНИЕ НА ЭКРАНЕ
        # -----------------------------------------------------

        await interaction.response.send_message(
            "✅ **Заявка отправлена!**\n\n"
            f"🎖️ Звание: **{rank}**\n"
            f"🪪 Номер удостоверения: `{badge_number}`\n"
            "📎 Док-ва получены.\n\n"
            "📋 Заявка отправлена модераторам.",
            ephemeral=True
        )


# =========================================================
# КНОПКА «ЗАПРОСИТЬ РОЛЬ»
# =========================================================

class RequestRoleButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Запросить роль",
            emoji="📝",
            style=discord.ButtonStyle.primary,
            custom_id="gibdd_request_role"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Эта кнопка работает только на сервере.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ApplicationModal()
        )


# =========================================================
# ОСНОВНАЯ ПАНЕЛЬ
# =========================================================

class RoleRequestView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            RequestRoleButton()
        )


# =========================================================
# ПОЛУЧЕНИЕ КАНДИДАТА ИЗ ЗАЯВКИ
# =========================================================

async def process_application(
    interaction: discord.Interaction,
    approved: bool
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
            "❌ У вас нет прав для обработки заявок.",
            ephemeral=True
        )

        return

    guild = interaction.guild

    message = interaction.message

    if (
        guild is None
        or message is None
        or not message.embeds
    ):

        await interaction.response.send_message(
            "❌ Не удалось прочитать заявку.",
            ephemeral=True
        )

        return

    embed = message.embeds[0]

    candidate_value = get_embed_field(
        embed,
        "👤 Кандидат"
    )

    badge_value = get_embed_field(
        embed,
        "🪪 Номер удостоверения"
    )

    proof_value = get_embed_field(
        embed,
        "📎 Док-ва, что вы сотрудник ГИБДД"
    )

    rank = get_rank_from_embed(
        embed
    )

    candidate_id = parse_user_id(
        candidate_value
    )

    if candidate_id is None:

        await interaction.response.send_message(
            "❌ Не удалось определить кандидата.",
            ephemeral=True
        )

        return

    if rank not in RANK_ROLES:

        await interaction.response.send_message(
            "❌ Не удалось определить звание.",
            ephemeral=True
        )

        return

    member = guild.get_member(
        candidate_id
    )

    if member is None:

        try:

            member = await guild.fetch_member(
                candidate_id
            )

        except Exception:

            member = None

    roles = get_rank_roles(
        guild,
        rank
    )

    if not roles:

        await interaction.response.send_message(
            "❌ Роли выбранного звания не найдены.",
            ephemeral=True
        )

        return

    # =====================================================
    # ПРИНЯТИЕ
    # =====================================================

    if approved:

        if member is None:

            await interaction.response.send_message(
                "❌ Кандидат больше не находится на сервере.",
                ephemeral=True
            )

            return

        bot_member = guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ Не удалось определить роль бота.",
                ephemeral=True
            )

            return

        impossible_roles = [
            role
            for role in roles
            if role >= bot_member.top_role
        ]

        if impossible_roles:

            await interaction.response.send_message(
                "❌ Бот не может выдать роли:\n\n"
                + "\n".join(
                    f"• **{role.name}**"
                    for role in impossible_roles
                )
                + "\n\n"
                "Подними роль бота выше ролей ГИБДД.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # ВЫДАЁМ РОЛИ
        # -------------------------------------------------

        try:

            roles_to_add = [
                role
                for role in roles
                if role not in member.roles
            ]

            if roles_to_add:

                await member.add_roles(
                    *roles_to_add,
                    reason=(
                        f"Заявка ГИБДД одобрена | "
                        f"Звание: {rank}"
                    )
                )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Discord запретил выдачу ролей.\n\n"
                "Проверь право **Управление ролями** "
                "и иерархию ролей.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                f"❌ Ошибка выдачи ролей: `{error}`",
                ephemeral=True
            )

            return

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in roles
        )

        # -------------------------------------------------
        # АУДИТ
        # -------------------------------------------------

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
                    "🎖️ Звание",
                    f"**{rank}**",
                    True
                ),
                (
                    "🪪 Номер удостоверения",
                    badge_value or "Не указан",
                    True
                ),
                (
                    "📎 Док-ва, что вы сотрудник ГИБДД",
                    proof_value or "Не указаны",
                    False
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
            ]
        )

        # -------------------------------------------------
        # ОБНОВЛЯЕМ ЗАЯВКУ
        # -------------------------------------------------

        embed.color = discord.Color.green()

        embed.add_field(
            name="📊 Результат",
            value=(
                "🟢 **ПРИНЯТ**\n"
                f"Модератор: {interaction.user.mention}"
            ),
            inline=False
        )

        try:

            await message.edit(
                embed=embed,
                view=None
            )

        except discord.HTTPException:

            pass

        await interaction.response.send_message(
            "✅ **Заявка принята!**\n\n"
            f"👤 {member.mention}\n"
            f"🎖️ Звание: **{rank}**\n\n"
            "🎭 Роли выданы.\n"
            "📋 Запись отправлена в кадровый аудит.",
            ephemeral=True
        )

        return

    # =====================================================
    # ОТКЛОНЕНИЕ
    # =====================================================

    await send_audit(
        guild,
        "🔴 КАДРОВЫЙ АУДИТ — ОТКЛОНЁН",
        discord.Color.red(),
        [
            (
                "👤 Кандидат",
                candidate_value or f"`{candidate_id}`",
                False
            ),
            (
                "🎖️ Звание",
                f"**{rank}**",
                True
            ),
            (
                "🪪 Номер удостоверения",
                badge_value or "Не указан",
                True
            ),
            (
                "📎 Док-ва, что вы сотрудник ГИБДД",
                proof_value or "Не указаны",
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
        ]
    )

    embed.color = discord.Color.red()

    embed.add_field(
        name="📊 Результат",
        value=(
            "🔴 **ОТКЛОНЁН**\n"
            f"Модератор: {interaction.user.mention}"
        ),
        inline=False
    )

    try:

        await message.edit(
            embed=embed,
            view=None
        )

    except discord.HTTPException:

        pass

    await interaction.response.send_message(
        "❌ **Заявка отклонена.**\n\n"
        "📋 Запись отправлена в кадровый аудит.",
        ephemeral=True
    )


# =========================================================
# КНОПКА ПРИНЯТЬ
# =========================================================

class ApproveButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Принять",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id="gibdd_application_approve"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await process_application(
            interaction,
            True
        )


# =========================================================
# КНОПКА ОТКЛОНИТЬ
# =========================================================

class RejectButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Отклонить",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id="gibdd_application_reject"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await process_application(
            interaction,
            False
        )


# =========================================================
# ПАНЕЛЬ МОДЕРАЦИИ
# =========================================================

class ModerationView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            ApproveButton()
        )

        self.add_item(
            RejectButton()
        )


# =========================================================
# /SETUP_ROLES
# =========================================================

@bot.tree.command(
    name="setup_roles",
    description="Создать панель запроса роли ГИБДД"
)
@app_commands.guilds(
    discord.Object(
        id=GUILD_ID
    )
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

    if interaction.channel is None:

        await interaction.response.send_message(
            "❌ Не удалось определить канал.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title="🟡 Lipton | ГИБДД",
        description=(
            "## 🎖️ Запрос роли\n\n"
            "Нажмите **📝 Запросить роль**.\n\n"
            "После нажатия откроется отдельное "
            "popup-окно Discord.\n\n"
            "**В окне необходимо:**\n"
            "🎖️ Указать звание\n"
            "🪪 Указать номер удостоверения\n"
            "📎 Указать ссылку или номер удостоверения "
            "в поле «Док-ва, что вы сотрудник ГИБДД»\n\n"
            "📋 После отправки заявка поступит модераторам."
        ),
        color=discord.Color.gold()
    )

    await interaction.channel.send(
        embed=embed,
        view=RoleRequestView()
    )

    await interaction.response.send_message(
        "✅ Панель запроса ролей успешно отправлена!",
        ephemeral=True
    )


# =========================================================
# СОБЫТИЯ И ЗАПУСК БОТА
# =========================================================

@bot.event
async def on_ready():
    # Регистрация persistent-view, чтобы кнопки работали после перезапуска бота
    bot.add_view(RoleRequestView())
    bot.add_view(ModerationView())

    # Синхронизируем slash-команды
    try:

        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Бот запущен под именем: {bot.user}")
        print("✅ Команды и persistent views успешно синхронизированы.")

    except Exception as e:

        print(f"❌ Ошибка при синхронизации команд: {e}")


if __name__ == "__main__":
    bot.run(TOKEN)
