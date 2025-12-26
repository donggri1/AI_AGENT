""""
LangGraph

-state : 노드 간 공유되는 상태 정보
-Node : 실제 작업을 수행하는 함수
-Edge : 노드 간의 연결을 나타내며, 데이터 흐름을 정의
-Graph : 노드와 엣지로 구성된 전체 구조를 나타내며, 작업의 흐름을 관리

"""
import os
from typing_extensions import TypedDict
from telegram import Update

from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,MessageHandler,filters
from env import TELEGRAM_BOT_TOKEN,GEMINI_API_KEY
from chatbot_crew import ChatBotCrew,add_to_conversation,get_conversation_context


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message is None or update.message.text is None:
        return

    user_message = update.message.text
    chatbot_crew = ChatBotCrew()
    result = chatbot_crew.crew().kickoff(inputs={"message": user_message})

    bot_response = result.raw
    add_to_conversation(user_message , bot_response)


    await update.message.reply_text(bot_response)



app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# app.add_handler(CommandHandler("hello", hello))

app.add_handler(MessageHandler(filters.TEXT, handler))

app.run_polling()
