import os
from urllib.parse import urlparse

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
        1533075722330046484,
        1533075702432403456,
        1533075739631550494,
    ],
    "Старшина": [
        1533075777179095212,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075702432403456,
        1533075739631550494,
    ],
    "Прапорщик": [
        1533075775777931385,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075702432403456,
        1533075739631550494,
    ],
    "Ст прапорщик": [
        1533075774134026350,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075702432403456,
        1533075739631550494,
    ],
    "Младший лейтенант": [
        1533075772950974474,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075702432403456,
        1533075739631550494,
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
        1533075731054071959,
        1533075702432403456,
        1533075739631550494,
    ],
    "Капитан": [
        1533075768760991934,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075702432403456,
        1533075739631550494,
    ],
    "Майор": [
        1533075759583723681,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
        1533075692785504327,
        1533075702432403456,
    ],
    "Подполковник": [
        1533075757608337538,
        1533075786175746108,
        1533075784858865704,
        1533075745751175299,
        1533075731054071959,
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
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# ПРОВЕРКА МОДЕРАТОРА
# =========================================================

def is_moderator(member: discord.Member) -> bool:
    return (
        member.guild_permissions.administrator
        or any(role.id == MODERATOR_ROLE_ID for role in member.roles)
    )


# =========================================================
# ПОЛУЧЕНИЕ РОЛЕЙ ЗВАНИЯ
# =========================================================

def get_rank_roles(guild: discord.Guild, rank: str):
    roles = []
    seen = set()

    for role_id in RANK_ROLES.get(rank, []):
        role = guild.get_role(int(role_id))
        if role is not None and role.id not in seen:
            roles.append(role)
            seen.add(role.id)

    return roles


# =========================================================
# ПРОВЕРКА ДОКАЗАТЕЛЬСТВА
# =========================================================

def normalize_proof(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Док-ва обязательны.")

    # Разрешаем либо ссылку, либо номер удостоверения.
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return value
        raise ValueError("Укажите корректную ссылку на доказательство.")

    # Если это не URL — считаем, что пользователь указал номер удостоверения.
    cleaned = value.replace(" ", "").replace("-", "")
    if not cleaned.isdigit():
        raise ValueError(
            "В поле док-в укажите ссылку (https://...) "
            "или только номер удостоверения."
        )

    return value


# =========================================================
# КАДРОВЫЙ АУДИТ
# =========================================================

async def send_audit(
    guild: discord.Guild,
    title: str,
    color: discord.Color,
    fields: list,
    proof: str | None = None
):
    channel = guild.get_channel(AUDIT_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(AUDIT_CHANNEL_ID)
        except Exception as error:
            print(f"❌ Канал кадрового аудита не найден: {error}")
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

    if proof:
        if proof.startswith(("http://", "https://")):
            embed.add_field(
                name="📎 Док-ва, что сотрудник ГИБДД",
                value=f"[Открыть доказательство]({proof})",
                inline=False
            )
        else:
            embed.add_field(
                name="📎 Док-ва, что сотрудник ГИБДД",
                value=f"Номер: `{proof}`",
                inline=False
            )

    embed.set_footer(
        text="Lipton | ГИБДД • Кадровый аудит"
    )

    try:
        await channel.send(embed=embed)
        return True
    except discord.Forbidden:
        print("❌ У бота нет прав писать в кадровый аудит.")
        return False
    except discord.HTTPException as error:
        print(f"❌ Ошибка отправки аудита: {error}")
        return False


# =========================================================
# POPUP — ЗАЯВКА В ГИБДД
# =========================================================

class ApplicationModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="🎖 Заявка на роль ГИБДД",
            timeout=300
        )

        # -------------------------------------------------
        # ЗВАНИЕ — ТОЛЬКО ВЫБОР
        # -------------------------------------------------
        rank_options = [
            discord.SelectOption(
                label=rank,
                value=rank
            )
            for rank in RANK_ROLES
        ]

        self.rank_select = discord.ui.Select(
            custom_id="gibdd_apply_rank",
            placeholder="Выберите звание...",
            options=rank_options,
            min_values=1,
            max_values=1,
            required=True
        )

        self.add_item(
            discord.ui.Label(
                text="🎖 Звание",
                description="Выберите запрашиваемое звание",
                component=self.rank_select
            )
        )

        # -------------------------------------------------
        # НОМЕР УДОСТОВЕРЕНИЯ — ВВОД
        # -------------------------------------------------
        self.badge_number = discord.ui.TextInput(
            custom_id="gibdd_badge_number",
            placeholder="Например: 01427",
            min_length=1,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )

        self.add_item(
            discord.ui.Label(
                text="🪪 Номер удостоверения",
                description="Укажите номер своего удостоверения ГИБДД",
                component=self.badge_number
            )
        )

        # -------------------------------------------------
        # ДОКАЗАТЕЛЬСТВО — ССЫЛКА ИЛИ НОМЕР
        # -------------------------------------------------
        self.proof = discord.ui.TextInput(
            custom_id="gibdd_proof",
            placeholder="Ссылка на документ или номер удостоверения",
            min_length=1,
            max_length=500,
            required=True,
            style=discord.TextStyle.paragraph
        )

        self.add_item(
            discord.ui.Label(
                text="📎 Док-ва, что вы сотрудник ГИБДД",
                description="Укажите ссылку на документ или номер удостоверения. Фото отправлять не нужно.",
                component=self.proof
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Заявка доступна только на сервере.",
                ephemeral=True
            )
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "❌ Не удалось определить участника сервера.",
                ephemeral=True
            )
            return

        rank = self.rank_select.values[0]
        badge_number = str(self.badge_number.value).strip()

        try:
            proof = normalize_proof(str(self.proof.value))
        except ValueError as error:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )
            return

        moderation_channel = interaction.guild.get_channel(
            MODERATION_CHANNEL_ID
        )

        if moderation_channel is None:
            try:
                moderation_channel = await bot.fetch_channel(
                    MODERATION_CHANNEL_ID
                )
            except Exception:
                await interaction.response.send_message(
                    "❌ Канал для заявок не найден.",
                    ephemeral=True
                )
                return

        rank_roles = get_rank_roles(
            interaction.guild,
            rank
        )

        if not rank_roles:
            await interaction.response.send_message(
                "❌ Для выбранного звания не найдены роли.\n\n"
                f"🎖 Звание: **{rank}**\n"
                "Проверьте ID ролей в `RANK_ROLES`.",
                ephemeral=True
            )
            return

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in rank_roles
        )

        embed = discord.Embed(
            title="📝 НОВАЯ ЗАЯВКА В ГИБДД",
            description=(
                "Проверьте данные кандидата.\n\n"
                "Заявка оформлена через приватное popup-окно Discord."
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
            name="🎖 Звание",
            value=f"**{rank}**",
            inline=True
        )

        embed.add_field(
            name="🪪 Номер удостоверения",
            value=f"`{badge_number}`",
            inline=True
        )

        embed.add_field(
            name="🎭 Роли для выдачи",
            value=roles_text,
            inline=False
        )

        if proof.startswith(("http://", "https://")):
            embed.add_field(
                name="📎 Док-ва, что вы сотрудник ГИБДД",
                value=f"[Открыть доказательство]({proof})",
                inline=False
            )
        else:
            embed.add_field(
                name="📎 Док-ва, что вы сотрудник ГИБДД",
                value=f"Номер удостоверения: `{proof}`",
                inline=False
            )

        embed.set_footer(
            text="Lipton | ГИБДД • Кадровая заявка"
        )

        try:
            sent_message = await moderation_channel.send(
                embed=embed,
                view=ModerationView(
                    user_id=interaction.user.id,
                    badge_number=badge_number,
                    rank=rank,
                    role_ids=[role.id for role in rank_roles],
                    proof=proof
                )
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Бот не может отправить заявку в канал модерации.",
                ephemeral=True
            )
            return
        except discord.HTTPException as error:
            await interaction.response.send_message(
                f"❌ Discord не принял заявку: `{error}`",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ **Заявка оформлена**\n\n"
            f"🎖 Звание: **{rank}**\n"
            f"🪪 Номер удостоверения: `{badge_number}`\n\n"
            "📋 Заявка отправлена на проверку модератору.\n"
            "📎 Фото прикладывать не требуется.",
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

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Эта кнопка работает только на сервере.",
                ephemeral=True
            )
            return

        # Настоящее popup-окно Discord — ничего не отправляется в чат.
        await interaction.response.send_modal(
            ApplicationModal()
        )


# =========================================================
# ОСНОВНАЯ ПАНЕЛЬ
# =========================================================

class RoleRequestView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RequestRoleButton())


# =========================================================
# КНОПКА ПРИНЯТЬ
# =========================================================

class ApproveButton(discord.ui.Button):

    def __init__(
        self,
        user_id: int,
        badge_number: str,
        rank: str,
        role_ids: list[int],
        proof: str
    ):
        self.user_id = user_id
        self.badge_number = badge_number
        self.rank = rank
        self.role_ids = role_ids
        self.proof = proof

        super().__init__(
            label="Принять",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id=f"approve:{user_id}:{rank}"
        )

    async def callback(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return

        if not is_moderator(interaction.user):
            await interaction.response.send_message(
                "❌ У тебя нет прав для обработки заявок.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        member = guild.get_member(self.user_id)
        if member is None:
            await interaction.response.send_message(
                "❌ Пользователь не найден на сервере.",
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

        roles_to_give = []
        for role_id in self.role_ids:
            role = guild.get_role(role_id)
            if role is not None and role not in roles_to_give:
                roles_to_give.append(role)

        if not roles_to_give:
            await interaction.response.send_message(
                "❌ Роли выбранного звания не найдены.",
                ephemeral=True
            )
            return

        # Проверяем все роли до выдачи.
        for role in roles_to_give:
            if role.is_default():
                continue
            if role >= bot_member.top_role or not role.is_assignable():
                await interaction.response.send_message(
                    f"❌ Бот не может выдать роль **{role.name}**.\n\n"
                    "Подними главную роль бота выше этой роли.",
                    ephemeral=True
                )
                return

        try:
            roles_already = [role for role in roles_to_give if role in member.roles]
            roles_missing = [role for role in roles_to_give if role not in member.roles]

            if roles_missing:
                await member.add_roles(
                    *roles_missing,
                    reason=f"Заявка ГИБДД одобрена. Звание: {self.rank}"
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord запретил выдачу роли.\n\n"
                "Проверь право **Управление ролями** и положение ролей бота.",
                ephemeral=True
            )
            return
        except discord.HTTPException as error:
            await interaction.response.send_message(
                f"❌ Ошибка Discord: `{error}`",
                ephemeral=True
            )
            return

        roles_text = "\n".join(
            f"• {role.mention}"
            for role in roles_to_give
        )

        await send_audit(
            guild,
            "🟢 КАДРОВЫЙ АУДИТ — ПРИНЯТ",
            discord.Color.green(),
            [
                (
                    "👤 Сотрудник",
                    f"{member.mention}\n`{member.id}`",
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
            self.proof
        )

        embed = interaction.message.embeds[0]
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
            await interaction.message.edit(
                embed=embed,
                view=None
            )
        except discord.HTTPException:
            pass

        await interaction.response.send_message(
            "✅ **Заявка принята!**\n\n"
            f"👤 {member.mention}\n"
            f"🎖 Звание: **{self.rank}**\n"
            f"🪪 Удостоверение: `{self.badge_number}`\n\n"
            f"🎭 Выданы роли:\n{roles_text}\n\n"
            "📋 Запись отправлена в кадровый аудит.",
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
        role_ids: list[int],
        proof: str
    ):
        self.user_id = user_id
        self.badge_number = badge_number
        self.rank = rank
        self.role_ids = role_ids
        self.proof = proof

        super().__init__(
            label="Отклонить",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id=f"reject:{user_id}:{rank}"
        )

    async def callback(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return

        if not is_moderator(interaction.user):
            await interaction.response.send_message(
                "❌ У тебя нет прав для обработки заявок.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        member = guild.get_member(self.user_id)
        member_text = (
            f"{member.mention}\n`{member.id}`"
            if member else f"`{self.user_id}`"
        )

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
            self.proof
        )

        embed = interaction.message.embeds[0]
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
            await interaction.message.edit(
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
# VIEW МОДЕРАЦИИ
# =========================================================

class ModerationView(discord.ui.View):

    def __init__(
        self,
        user_id: int,
        badge_number: str,
        rank: str,
        role_ids: list[int],
        proof: str
    ):
        super().__init__(timeout=None)

        self.add_item(
            ApproveButton(
                user_id,
                badge_number,
                rank,
                role_ids,
                proof
            )
        )

        self.add_item(
            RejectButton(
                user_id,
                badge_number,
                rank,
                role_ids,
                proof
            )
        )


# =========================================================
# КОМАНДА /SETUP_ROLES
# =========================================================

@bot.tree.command(
    name="setup_roles",
    description="Создать панель запроса роли ГИБДД"
)
async def setup_roles(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member):
        return

    if not is_moderator(interaction.user):
        await interaction.response.send_message(
            "❌ У тебя нет прав для этой команды.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🟡 Lipton | ГИБДД",
        description=(
            "## 🎖 Запрос роли\n\n"
            "Нажмите **📝 Запросить роль**, чтобы открыть "
            "приватное окно оформления заявки.\n\n"
            "**В меню нужно:**\n"
            "🎖 Выбрать звание\n"
            "🪪 Написать номер удостоверения\n"
            "📎 Указать ссылку или номер удостоверения "
            "в разделе **«Док-ва, что вы сотрудник ГИБДД»**\n\n"
            "📷 **Фото отправлять не нужно.**\n"
            "После проверки модератором будут выданы роли."
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
    if not getattr(bot, "_views_added", False):
        bot.add_view(RoleRequestView())
        bot._views_added = True

    try:
        synced = await bot.tree.sync()
        print(f"✅ Бот запущен: {bot.user}")
        print(f"✅ Slash-команд синхронизировано: {len(synced)}")
    except Exception as error:
        print(f"❌ Ошибка синхронизации: {error}")


# =========================================================
# ЗАПУСК
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "❌ Не задан DISCORD_TOKEN. "
        "Установи переменную окружения DISCORD_TOKEN."
    )

bot.run(TOKEN)

if __name__ == "__main__":
    bot.run(TOKEN)
