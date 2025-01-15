import os
from aiogram.types import Message, InputMediaPhoto, ReactionTypeEmoji, InputMediaDocument

from app.external_connections.ops_pa import PGAnswer, PG_PAYMENT_TYPE, PG_TRX_STATUS
from app.external_connections.clickup import CLICKUP_CLIENT
from app.external_connections.postgres import POSTGRES, PostgresShop

async def beh_send_auto_ticket(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text: str) -> bool:
    if message.content_type not in ['photo', 'document']:
        await message.reply("@Serggiant, have a look \n @Serggiant, проверь этот запрос")
        print('No valid attachments found')
        return False

    media_group = []
    local_file_paths = []

    try:
        if message.photo:
            last_photo = message.photo[-1]
            screenshot_url = last_photo.file_id

            if screenshot_url:
                media_group.append(InputMediaPhoto(
                    media=screenshot_url,
                    caption=f"New ticket by transaction ID: {trx_details.trx_id}"
                ))

                file = await message.bot.get_file(screenshot_url)
                if not os.path.exists("tmp/img/"):
                    os.makedirs("tmp/img/")
                file_local_path = f"tmp/img/ss{trx_details.trx_id}.jpg"
                await message.bot.download_file(file.file_path, file_local_path)
                local_file_paths.append(file_local_path)
            else:
                print("No screenshot available")

        if message.document:
            document = message.document
            doc_file_id = document.file_id
            doc_file_name = document.file_name

            media_group.append(InputMediaDocument(
                media=doc_file_id,
                caption=f"New ticket by transaction ID: {trx_details.trx_id}" if not media_group else None
            ))

            file = await message.bot.get_file(doc_file_id)
            if not os.path.exists("tmp/docs/"):
                os.makedirs("tmp/docs/")
            file_local_path = f"tmp/docs/{trx_details.trx_id}_{doc_file_name}"
            await message.bot.download_file(file.file_path, file_local_path)
            local_file_paths.append(file_local_path)

        if not media_group:
            await message.reply("@Serggiant, have a look \n @Serggiant, проверь этот запрос")
            print('No valid media found')
            return False

        terminal_index = 666
        provider = POSTGRES.get_provider_by_terminal_index(terminal_index)
        if provider is None:
            await message.reply("@Serggiant, I couldn't solve i \n @Serggiant, проверь этот запрос")
            print(f"State 666. Trx {trx_details.trx_id}, didn't find provider by terminal_id: {terminal_index}")
            return False

        prov_messages = await message.bot.send_media_group(
            chat_id=provider.support_chat_id,
            media=media_group
        )

        cu_data = await CLICKUP_CLIENT.create_auto_task(
            list_id=provider.cu_list_id,
            attachments=local_file_paths, 
            pg_trx_id=trx_details.trx_id
        )

        db_ticket_request_success = POSTGRES.create_new_ticket_request(
            trx_id=trx_details.trx_id,
            shop_data=shop,
            shop_mes_id=message.message_id,
            provider_data=provider,
            provider_mes_id=prov_messages[0].message_id,
            cu_task_id=cu_data['id'],
            is_manual_ticket=False,
            message_full_text=message_full_text
        )

        await message.react(reaction=[ReactionTypeEmoji(emoji="👀")])
        return db_ticket_request_success

    finally:
        for file_path in local_file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing temporary file {file_path}: {e}")