from aiogram.types import ReactionTypeEmoji
from app.external_connections.postgres import POSTGRES

async def check_message_reactions(bot, chat_id: int, message_id: int) -> bool:

   try:
       reactions = await bot.get_message_reactions(chat_id, message_id)
       
       if not reactions or not reactions.reactions:
           return True

       has_only_eye = True
       for reaction in reactions.reactions:
           if isinstance(reaction.type, ReactionTypeEmoji):
               if reaction.type.emoji != "👀":
                   has_only_eye = False
                   break
       
       return has_only_eye

   except Exception as e:
       print(f"Error checking reactions: {e}")
       return False

async def check_pending_messages(bot):

   try:
       pending_messages = POSTGRES.get_all_tickets_v2()
       
       for ticket in pending_messages:
           needs_attention = await check_message_reactions(
               bot, 
               -1002323088756,
               ticket.provider_message_id
           )
           
           if needs_attention:
               
               await bot.send_message(
                   chat_id=ticket.provider_message_id, 
                   text="@P2m_payin_support @KINGK4249 Please check this ticket",
                   reply_to_message_id=ticket.provider_message_id
               )
               print('Needs attentions')
           else:
               print('Doesnt need attention')
               
   except Exception as e:
       print(f"Error in check_pending_messages: {e}")