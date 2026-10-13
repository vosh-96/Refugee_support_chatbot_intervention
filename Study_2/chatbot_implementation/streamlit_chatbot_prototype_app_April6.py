### Set Up #######
# allows my code to make http requests

import streamlit as st
import requests
import os
from together import Together
import uuid
from gsheet_logger import log_exchange
import random
import urllib.parse

# connection to data sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1EEyvIg_jbH2uuP2285H9rV22bPBXao2ZIPub7xKNU1M/edit?gid=0#gid=0"

#sessionID
if "session_id" not in st.session_state:
  import uuid
  st.session_state["session_id"] = str(uuid.uuid4())

## prolific parameters
# st.query_params returns a dict-like object directly

# Store them in session_state for later use
if "prolific_pid" not in st.session_state:
  prolific_pid = st.query_params.get("PROLIFIC_PID", None)
  study_id = st.query_params.get("STUDY_ID", None)
  prolific_session_id = st.query_params.get("SESSION_ID", None)
  bot_name = st.query_params.get("BOT_NAME", "flyer")
  st.session_state["prolific_pid"] = prolific_pid
  st.session_state["prolific_study_id"] = study_id
  st.session_state["prolific_session_id"] = prolific_session_id
  st.session_state["bot_name"] = bot_name

if "enable_selection" not in st.session_state:
  enable_selection = st.query_params.get("enable_selection", "0")
  st.session_state["enable_selection"] = enable_selection

if "stage" not in st.session_state:
  st.session_state.stage = "intervention"

st.title ("Refugee Attitude Study")

if st.session_state.stage == "intervention":
  
  # Set environment variable for API key
  os.environ["TOGETHER_API_KEY"] = st.secrets["TOGETHER_API_KEY"]

  # API endpoint
  llm_model = "openai/gpt-oss-20b"

  client = Together() # auth defaults to os.environ.get("TOGETHER_API_KEY")

  # creating request data
  data = {
      "role": "user",     # which agent i want to use
      "content": "",      # Sending user message as a string in the input field
      "max_tokens": 30,   # limit answer length
      "temperature": 0.7, # balance between creativity and consistency
  }

  def ask_llm(user_message):
  # user_message - new message which we send to chatbot.

    data.update({
        "content": user_message,
    })

    try:
      # send request (sends data to the API and put answer into response)
      response = client.chat.completions.create(
          model=llm_model,
          messages=[ data ]
      )
      return response.choices[0].message.content
    except Exception as e:
      # The exception message may include status or error details
      return (f"Error: {e}")

  #Define variable conditions
  conditions = ["roleplay", "debunking", "interview", "empathy", "neutral", "flyer"]

  #only for development phase/testing. 
  #only show condition selection if it hasnt been set yet
  if st.session_state.enable_selection == "1":
    if "condition" not in st.session_state:
      selected_condition = st.selectbox("Choose the chatbot condition to test:", conditions)
      if st.button("Start chatbot"):
        st.session_state.condition = selected_condition
  
  ##randomly assign participant condition (stored in session_state so it persists)
  if st.session_state.enable_selection == "0":
    if "condition" not in st.session_state:
      st.session_state.condition = st.session_state.bot_name

  if "condition" in st.session_state:
    condition = st.session_state.condition
    #st.write(f"Assigned condition: {condition}")
  else:
    condition = ""

  if "vars_init_done" not in st.session_state or not st.session_state.vars_init_done:
    # here is initialization for all global variables in the session_state
    st.session_state.messages = []
    st.session_state.round = 0
    st.session_state.subturn = False
    st.session_state.started = False   
    st.session_state.ended = False   
    st.session_state.init_task = False

    st.session_state.vars_init_done = True

  # add progress bar
  def show_progress(current_round: int, total_rounds: int):
    progress = current_round / total_rounds
    st.progress(progress)
    #st.caption(f"Round {current_round} of {total_rounds}")


  ###Treatment Group1: Roleplay Chatbot###
  if condition == "roleplay":

    #total rounds
    total_rounds = 7

    # mobile friendly
    st.set_page_config(
      page_title ="Roleplay Chatbot",
      layout="wide",
      initial_sidebar_state="collapsed"
    )
    #streamlit UI
    st.title("Roleplay Chatbot")

    if not st.session_state.init_task:
      # add system role/facilitator introduction
      # do it also only once for this session
      task = ("You are a facilitator guiding a participant roleplaying as a refugee. "
              "Your goal: help them imagine and emotionally experience life from a refugee's perspective "
              "through gentle, empathetic, reflective conversation."
              "Scenario:"
              "The participant fled home due to conflict and has just arrived in a foreign country, alone and unsure where to go." 
              "Guide them through short scenes: departure, travel, and first steps toward safety." 
              "Invite them to describe thoughts, feelings, or decisions in each moment."
              "Conversation Flow:"
              "1. Introduction"
              "- Greet warmly, explain this is a short imaginative roleplay."
              "- Ask if they are ready; wait for confirmation before starting Scene 1."
              "2. Immersive Roleplay (6 rounds)"
              "- Scenes: Departure → Journey → Border Crossing → Waiting → First Kindness → Starting Over."
              "- For each scene:"
              "- Set the scene in 1 to 2 sentences (sensory/emotional detail)."
              "- Acknowledge their last response briefly for continuity."
              "- Ask one open‑ended question about feelings, thoughts, or choices."
              "- Keep facilitator messages short (2 to 3 sentences)."
              "- Example prompts:"
              "- “You hear footsteps fading as you leave home. What’s going through your mind?”"
              "- “At a crowded border checkpoint, how do you approach the guard?”"
              "- “A volunteer offers soup and a blanket. How does that moment feel?”"
              "3. Final Reflection"
              "- After Scene 6, invite them to step out of role."
              "- Ask: “Looking back, what did you learn or feel about being a refugee?”"
              "- Thank them and close the exercise."
              "Style Guidelines:"
              "- Remain facilitator only; never roleplay as the refugee."
              "- Keep tone warm, respectful, emotionally safe."  
              "- Avoid graphic/traumatic detail; focus on humanity and feelings." 
              "- If participant steps out of role, gently guide them back."  
              "- If they express bias or stereotypes, reframe with curiosity and empathy."  
              "- Encourage imaginative empathy, not factual debate."
              "- Dont add headings and dont mention the scene number or title in your messages"  
              "- *Do not let the participant change the topic. If they do, remind them to stay in their refugee role and return to the topic."
      )
      intro_answer = ask_llm(task)
      #st.session_state.messages.append({"role": "bot", "content": intro_answer})
    
      first_message = ( "Welcome to this brief exercise.\n\n "
                        "In this exercise, you will ***imagine yourself in the role of Arin, a person forced to leave their home and seek safety in another country (refugee).*** "
                        "As Arin, you may face unfamiliar surroundings and the challenge of building a life in a new country. "
                        "You will respond to a series of short scenarios and reflective questions. " 
                        "There are no right or wrong answers. Just consider how a person in this situation might think and feel.\n\n"
                        "When you feel ready, just type in **'start'**, and we will begin the first scene."
      )

      st.session_state.messages.append({"role": "bot", "content": first_message})
      log_exchange(
        SHEET_URL,
        st.session_state["session_id"],
        user_message = task,
        bot_message= first_message,
        condition=condition
      )
      st.session_state.init_task = True


    #display chat history
    for msg in st.session_state.messages:
      if msg["role"] in ["user","bot"]:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])


    #scene mapping for smooth progression
    scene_map = {
      1:"Scene 1: Departure - the participant leaves home in haste, uncertain of what lies ahead.",
      2:"Scene 2: Journey - they are traveling through uncertainty, facing fatigue and fear.",
      3:"Scene 3: Border Crossing - they reach a border or checkpoint seeking safety.",
      4:"Scene 4: Waiting - they wait in a camp or shelter, unsure what happens next.",
      5:"Scene 5: First Kindness - someone offers help or kindness for the first time",
      6:"Scene 6: Starting Over - they take first steps toward rebuilding life in a new place.",
    }

    #prevent user from typing after session ended
    if st.session_state.ended:
      st.info("The roleplay session has ended. Thank you for participating!")
      #st.stop()
    else:
      if prompt := st.chat_input("Type your message here..."):
        st.chat_message ("user").markdown(prompt)

        #detect 'ready to begin' prompt from user and start with 1st scene
        if not st.session_state.started and any (word in prompt.lower() for word in ["start"]):
          system_hint = ("The participant has confirmed they are ready." 
                          "Begin Scene 1: Departure."
                          "Set the moment of leaving home in 2 to 3 vivid sentences (sensory or emotional detail)." 
                          "Then ask one open, empathetic question about what the participant might be thinking or feeling." 
                          "Keep facilitator messages brief (2 to 3 sentences), warm, and supportive." 
                          "Do not add scene headings." 
                          "Do not roleplay as the refugee; remain in the facilitator role."
                        )
          st.session_state.messages.append({"role": "system", "content": system_hint})
          # initialize subturn and round
          st.session_state.subturn = False #next turn is scene intro
          st.session_state.round = 1
          st.session_state.started = True
        elif not st.session_state.started:
          st.chat_message("bot").markdown("Please type **'start'** to start the session!")
        
        if st.session_state.round > 0:
          st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.round == 7:
          #chat round 7: final reflection
          reflection_q = (
          "Our roleplay session is comming to an end. Looking back at this experience, what did you learn or realize about the life of refugees?"
          )
          st.chat_message("bot").markdown(reflection_q)
          st.session_state.messages.append({"role": "bot", "content": reflection_q})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message=reflection_q,
            condition= condition
          )
        elif st.session_state.round == 8:
          #chat round 8: closing message
          closing_msg = (
            "Thank you for participating! This concludes our roleplay session."
          )
          st.chat_message("bot").markdown(closing_msg)
          st.session_state.messages.append({"role": "bot", "content": closing_msg})
          st.session_state.ended = True

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message=closing_msg,
            condition= condition
          )
        elif 1 <= st.session_state.round <= 6:
          # scene hint
          current_scene= scene_map.get(st.session_state.round)
          #determine subturn
          if st.session_state.subturn:
            #reflection turn
            scene_hint = (
              "Connect briefly to the participant’s last response." 
              "Use 1 to 2 sentences to acknowledge, paraphrase, or show curiosity." 
              "Do not describe settings, environments, or new scenes during reflection." 
              "End with a short reflective prompt if needed, but never introduce sensory or narrative detail." 
              "Keep facilitator messages warm, brief, and supportive." 
              "Do not introduce or hint at the next scene." 
              "Pause after the reflective question and wait for the participant’s reply." 
              "Remain in the facilitator role; do not roleplay as the refugee." 
              "If the participant changes the topic, gently remind them to stay in their refugee role and return to the reflection."
            )
          else:
            #scene introduction turn
            scene_hint= (
              f"{current_scene}"
              "Introduce the next scene only after a reflection round has been completed." 
              "Reflection rounds are for acknowledging the participant’s response and prompting deeper thought — do not describe a new setting during reflection." 
              "Scene introductions must always include 2 to 3 vivid sentences of sensory or emotional detail to set the moment." 
              "Do not use repetitive descriptions"
              "Do not mention scene numbers or headings." 
              "Ask one short, open‑ended question about what they might think, feel, or decide in that moment." 
              "Remain in the facilitator role; do not roleplay as the refugee." 
              "If the participant changes the topic, gently remind them to stay in their refugee role and return to the scene."
            )
          st.session_state.messages.append({"role": "system", "content": scene_hint})

          #add system reminders for robustness
          if st.session_state.round in [3, 5]:
            system_reminder=(
              "Reminder: You are a facilitator guiding a refugee roleplay reflection." 
              "Stay empathetic, neutral, and supportive."
              "Always alternate: Scene round - Reflection round - Next scene." 
              "Never merge reflection and scene in the same message." 
              "Keep each facilitator message brief (2 to 3 sentences, no lists), empathetic, and supportive." 
              "Ask only one open, reflective question at a time." 
              "Do not give advice or solutions." 
              "Move naturally through the scenes." 
              "If the participant changes the topic, gently remind them to stay in their refugee role and return to the scene."
            )
            # add to conversation context but dont display it
            st.session_state.messages.append({"role": "system", "content": system_reminder})

          #build full conversation (so model sees context)
          conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
          ])

          bot_reply = ask_llm(conversation_text)

          st.chat_message("bot").markdown(bot_reply)
          st.session_state.messages.append({"role": "bot", "content": bot_reply})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message= bot_reply,
            condition= condition
          )

        if st.session_state.started:
          show_progress(st.session_state.round - 1, total_rounds)
          if st.session_state.subturn:
            st.session_state.round += 1
            if st.session_state.round < 7: # do not need subturns in step 7 and 8
              st.session_state.subturn = False # next turn will be scene intro
          else:
            st.session_state.subturn = True # next turn will be reflection

  ###Treatment Group2: Factual Debunking Chatbot ###
  elif condition == "debunking":

    #total rounds
    total_rounds = 7

    # mobile friendly
    st.set_page_config(
      page_title ="Factual Debunking Chatbot",
      layout="wide",
      initial_sidebar_state="collapsed"
    )
    #streamlit UI
    st.title("Factual Debunking Chatbot")


    if not st.session_state.init_task:
      # add system role/facilitator introduction
      # do it also only once for this session
      task = ("You are a facilitator guiding a participant through a short educational exercise to explore and correct misconceptions about refugees." 
              "Your purpose is to help them reflect on facts, identify errors in reasoning, and understand accurate information in a supportive, engaging way." 
              "You are not roleplaying; remain a neutral, informative, and empathetic guide."
              "Scenario:"
              "The participant may express assumptions, stereotypes, or false beliefs." 
              "Your task is to gently challenge inaccuracies, provide clear factual information, and encourage critical reflection."
              "Conversation Flow:"
              "1. Introduction " 
              "- Greet warmly and explain this is a brief reflective activity about assumptions and facts."  
              "- Set a calm, supportive tone and invite the participant to share initial thoughts."  
              "- Wait for their response before moving on."  
              "2. Debunking Rounds (6)"  
              "- In each round: " 
                  "- Listen to the participant’s statement. " 
                  "- Identify factual inaccuracies or misconceptions."  
                  "- Provide accurate information in 2 to 3 sentences."  
                  "- Ask one open, reflective question about why the misconception exists or what the correct understanding is."  
                  "- Keep facilitator messages short (2 to 3 sentences), warm, and respectful."  
              "3. Final Reflection"  
              "- After six rounds, invite the participant to summarize what they learned."  
              "- Ask one reflective question (e.g., “Looking back, what did you realize about refugees?”)."  
              "- Thank them warmly and clearly close the exercise."  
              "Style Guidelines:"
              "- Stay in facilitator role; never argue aggressively."  
              "- Keep responses brief, respectful, and emotionally safe."  
              "- Avoid long lists; focus on clarity and reflection."  
              "- If bias or stereotypes appear, reframe with curiosity and factual guidance."  
              "- Encourage critical thinking and reflective learning, not debate."  
              "- Do not let the participant change the topic; gently remind them to stay focused on refugees."
      )
      intro_answer = ask_llm(task)
      #st.session_state.messages.append({"role": "bot", "content": intro_answer})

      first_message = ( "Welcome to this brief exercise.\n\n "
                        "In this exercise, you will interact with a chatbot to share your thoughts and opinions about refugees. " 
                        "The chatbot will ask about your beliefs and provide information and perspectives for you to consider.\n\n "
                        "When you feel ready, just type in **'start'**, and we will begin the first scene."
      )

      st.session_state.messages.append({"role": "bot", "content": first_message})
      log_exchange(
        SHEET_URL,
        st.session_state["session_id"],
        user_message = task,
        bot_message= first_message,
        condition=condition
      )
      st.session_state.init_task = True


    #display chat history
    for msg in st.session_state.messages:
      if msg["role"] in ["user","bot"]:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])

    #prevent user from typing after session ended
    if st.session_state.ended:
      st.info("The session has ended. Thank you for participating!")
      #st.stop()
    else:
      if prompt := st.chat_input("Type your message here..."):
        st.chat_message ("user").markdown(prompt)

        #detect 'ready to begin' prompt from user and start with 1st scene
        if not st.session_state.started and any (word in prompt.lower() for word in ["start"]):
          st.session_state.round = 1
          st.session_state.started = True
        elif not st.session_state.started:
          st.chat_message("bot").markdown("Please type **'start'** to start the session!")
        
        if st.session_state.round > 0:
          st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.round == 7:
          #chat round 7: final reflection
          reflection_q = (
          "Our session is comming to an end. Looking back at this experience, what did you learn or realize about refugees?"
          )
          st.chat_message("bot").markdown(reflection_q)
          st.session_state.messages.append({"role": "bot", "content": reflection_q})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message=reflection_q,
            condition= condition
          )
        elif st.session_state.round == 8:
          #chat round 8: closing message
          closing_msg = (
            "Thank you for participating! This concludes our session."
          )
          st.chat_message("bot").markdown(closing_msg)
          st.session_state.messages.append({"role": "bot", "content": closing_msg})
          st.session_state.ended = True

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message=closing_msg,
            condition= condition
          )

        elif st.session_state.round == 1:
          start_msg = ( "Welcome! Please feel free to share any thoughts or concerns you may have about refugees.")
          st.chat_message ("bot").markdown(start_msg)
          st.session_state.messages.append({"role": "bot", "content" : start_msg})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message= start_msg,
            condition= condition
          )

        elif 1 <= st.session_state.round <= 6:
          scene_hint = (
            "Respond directly to the participant’s statement with calm, respectful factual reasoning." 
            "Blend short reflections or paraphrases with occasional open questions to prompt deeper thinking." 
            "Do not ask a question every turn; alternate between statements and questions to keep the flow conversational." 
            "When asking, use only one open question at a time." 
            "Keep responses brief (2 to 3 sentences)." 
            "If the participant changes the topic, gently remind them to stay focused on refugees."
          )
          st.session_state.messages.append({"role": "system", "content": scene_hint})
          
          #add system reminders for robustness
          if st.session_state.round in [3, 5]:
            system_reminder=(
              "Reminder: You are a facilitator guiding a factual reflection discussion." 
              "Stay neutral, informative, and supportive." 
              "Respond directly to participant statements with brief factual reasoning (2 to 3 sentences)." 
              "Blend short affirmations or reflections with occasional open questions to keep the dialogue natural." 
              "Encourage the participant to consider why a misconception exists and what the correct understanding is." 
              "If the participant asks a question, answer it directly before inviting reflection." 
              "Do not give advice or solutions." 
              "Keep responses brief (2 to 3 sentences, no lists)." 
              "If the participant changes the topic, gently remind them to stay focused on refugees."
            )
            # add to conversation context but dont display it
            st.session_state.messages.append({"role": "system", "content": system_reminder})

          #build full conversation (so model sees context)
          conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
          ])

          bot_reply = ask_llm(conversation_text)

          st.chat_message("bot").markdown(bot_reply)
          st.session_state.messages.append({"role": "bot", "content": bot_reply})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message= bot_reply,
            condition= condition
          )

        if st.session_state.started:
          show_progress(st.session_state.round - 1, total_rounds)
          st.session_state.round += 1

  ###Treatment Group3: Interactive Interviewing Chatbot ###
  elif condition == "interview":

      #total rounds
    total_rounds = 7  

    # mobile friendly
    st.set_page_config(
      page_title ="Interactive Interviewing Chatbot",
      layout="wide",
      initial_sidebar_state="collapsed"
    )
    #streamlit UI
    st.title("Interactive Interviewing Chatbot")


    if not st.session_state.init_task:
      # add system role/facilitator introduction
      # do it also only once for this session
      task = ("You are a facilitator guiding a reflective conversation with a participant about issues related to refugees." 
              "Your goal is to help them explore and examine their own beliefs, attitudes, and reasoning through open-ended reflection." 
              "Do not provide new factual information or data; your role is to prompt critical thinking and self-reflection, not to educate or persuade."
              "Conversation Structure:"
              "1. Introduction" 
              "- Begin with a warm, neutral introduction explaining this is a brief reflective discussion about beliefs and perceptions related to refugees."  
              "- Set a calm, respectful tone and ask if they are ready to begin."  
              "- When the participant indicates readiness, start the first topic."  
              "2. Reflective Discussion (6 rounds)"  
              "- In each round:"  
                "- Ask one open, thought‑provoking question about their beliefs or assumptions."  
                "- Blend in short reflective statements (e.g., “That’s an interesting perspective”) to keep the flow conversational."  
                "- Gently explore inconsistencies or gaps in reasoning with follow‑ups, without confrontation or judgment."  
                "- Keep facilitator responses concise (2 to 3 sentences)."  
                "- Maintain a curious, empathetic tone."  
              "3. Final Reflection"  
              "- After the sixth topic, invite the participant to reflect on the discussion as a whole."  
              "- Ask a closing question such as: “Looking back, did anything make you think differently about your own views or assumptions?”"  
              "- Acknowledge their reflection warmly and thank them for taking part."  
              "Style Guidelines:"
              "- Stay neutral and non‑judgmental."  
              "- Do not introduce new facts, data, or statistics."  
              "- Use short, conversational messages (2 to 3 sentences)."  
              "- Mix gentle affirmations with questions to avoid a rigid interview feel."  
              "- Highlight inconsistencies through curiosity, not correction. " 
              "- Encourage introspection and open reflection at every stage."  
              "- If the participant changes the topic, gently remind them to stay focused on refugees."
      )
      intro_answer = ask_llm(task)
      #st.session_state.messages.append({"role": "bot", "content": intro_answer})

      first_message = ( "Welcome to this brief exercise.\n\n "
                        "In this exercise, you will interact with a chatbot to answer questions about your thoughts and opinions regarding refugees. " 
                        "The chatbot will guide the conversation by asking questions and providing prompts for you to reflect on.\n\n "
                        "When you feel ready, just type in **'start'**, and we will begin the first scene."
      )

      st.session_state.messages.append({"role": "bot", "content": first_message})
      log_exchange(
        SHEET_URL,
        st.session_state["session_id"],
        user_message = task,
        bot_message= first_message,
        condition=condition
      )
      st.session_state.init_task = True


    #display chat history
    for msg in st.session_state.messages:
      if msg["role"] in ["user","bot"]:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])

    #prevent user from typing after session ended
    if st.session_state.ended:
      st.info("The session has ended. Thank you for participating!")
      #st.stop()
    else:
      if prompt := st.chat_input("Type your message here..."):
        st.chat_message ("user").markdown(prompt)

        #detect 'ready to begin' prompt from user and start with 1st scene
        if not st.session_state.started and any (word in prompt.lower() for word in ["start"]):
          st.session_state.round = 1
          st.session_state.started = True
        elif not st.session_state.started:
          st.chat_message("bot").markdown("Please type **'start'** to start the session!")

        if st.session_state.round > 0:
          st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.round == 7:
          #chat round 7: final reflection
          reflection_q = (
          "Our session is comming to an end. Looking back at this experience, what did you learn or realize about refugees?"
          )
          st.chat_message("bot").markdown(reflection_q)
          st.session_state.messages.append({"role": "bot", "content": reflection_q})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message=reflection_q,
            condition= condition
          )
        elif st.session_state.round == 8:
          #chat round 8: closing message
          closing_msg = (
            "Thank you for participating! This concludes our session."
          )
          st.chat_message("bot").markdown(closing_msg)
          st.session_state.messages.append({"role": "bot", "content": closing_msg})
          st.session_state.ended = True

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message=closing_msg,
            condition= condition
          )

        elif st.session_state.round == 1:
          start_msg = ( "Welcome! Please feel free to share any thoughts or concerns you may have about refugees.")
          st.chat_message ("bot").markdown(start_msg)
          st.session_state.messages.append({"role": "bot", "content" : start_msg})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message= start_msg,
            condition= condition
          )

        elif 1 <= st.session_state.round <= 6:
          scene_hint = (
            "Respond directly to the participant’s statement by briefly acknowledging their reasoning and inviting deeper reflection." 
            "Maintain a calm, neutral, and respectful tone." 
            "Blend short reflective statements (e.g., “That’s an interesting point”) with one open-ended question to explore their thoughts further." 
            "Always ask only one question at a time." 
            "Keep facilitator messages brief (2 to 3 sentences)." 
            "If the participant changes the topic, gently remind them to stay focused on refugees."
          )
          st.session_state.messages.append({"role": "system", "content": scene_hint})
          
          #add system reminders for robustness
          if st.session_state.round in [3, 5]:
            system_reminder=(
              "Reminder: You are a facilitator guiding a reflective conversation." 
              "Stay neutral, curious, and supportive." 
              "Help the participant examine their own beliefs and feelings through varied, natural responses." 
              "Alternate between brief acknowledgments, reflective statements, and occasional open questions to keep the flow conversational." 
              "Avoid repeating the same phrases; vary how you show empathy or curiosity." 
              "Not every turn needs a question — some can simply reflect or paraphrase the participant’s words." 
              "Do not give advice or solutions." 
              "Keep responses concise (2 to 3 sentences maximum, no lists)." 
              "If the participant changes the topic, gently remind them to stay focused on refugees."
            )
            # add to conversation context but dont display it
            st.session_state.messages.append({"role": "system", "content": system_reminder})

          #build full conversation (so model sees context)
          conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
          ])

          bot_reply = ask_llm(conversation_text)

          st.chat_message("bot").markdown(bot_reply)
          st.session_state.messages.append({"role": "bot", "content": bot_reply})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message= bot_reply,
            condition= condition
          )

        if st.session_state.started:
          show_progress(st.session_state.round - 1, total_rounds)
          st.session_state.round += 1

  ### Treatment Group 4: Empathetic Chatbot ###

  elif condition == "empathy":

    #total rounds
    total_rounds = 7

    # mobile friendly
    st.set_page_config(
      page_title ="Empathy Chatbot",
      layout="wide",
      initial_sidebar_state="collapsed"
    )
    #streamlit UI
    st.title("Empathy Chatbot")


    if not st.session_state.init_task:
      # add system role/facilitator introduction
      # do it also only once for this session
      task = ("You are a compassionate facilitator guiding participants toward a more empathetic attitude about refugees." 
              "Your role is to gently encourage emotional engagement with refugee experiences through warm validation, perspective‑taking, and reflective dialogue." 
              "Do not provide facts, corrections, or persuasion; focus only on empathy and human connection."
              "Conversation Flow:"
              "- Begin with a calm, neutral introduction that sets a supportive tone. Do not use phrases like “I’m glad you are here to reflect,” as participants are completing this as part of a study."  
              "- In each round: " 
                "- Acknowledge the participant’s response with varied, natural reflections (e.g., curiosity, empathy, paraphrasing)."  
                "- Ask one open‑ended question that invites them to imagine refugee experiences or emotions."  
                "- Occasionally use perspective‑taking prompts (e.g., “If you were in that position…”)."  
                "- Keep facilitator messages short (2 to 3 sentences), empathetic, and conversational.2 " 
              "- After several rounds, invite the participant to reflect on how their views or feelings may have shifted."  
              "- Thank them warmly and close the exercise."  
              "Style Guidelines:"
              "- Always remain empathetic, warm, and non‑judgmental."  
              "- Avoid roleplay, factual correction, or debate."  
              "- Do not introduce new facts, data, or statistics."  
              "- Blend short reflections with questions to keep the flow natural."  
              "- Encourage emotional openness and compassionate reflection at every stage."  
              "- Never confront, argue, or moralize."  
              "- If the participant changes the topic, gently remind them to stay focused on refugees."
      )
      intro_answer = ask_llm(task)
      #st.session_state.messages.append({"role": "bot", "content": intro_answer})

      first_message = ( "Welcome to this brief exercise.\n\n "
                        "In this exercise, you will engage in a brief conversation with a chatbot designed to facilitate empathetic reflection on issues related to refugees. " 
                        "The chatbot will guide the conversation by asking questions and providing prompts to thoughtfully reflect on your perspectives on refugees.\n\n "
                        "When you feel ready, just type in **'start'**, and we will begin the first scene."
      )

      st.session_state.messages.append({"role": "bot", "content": first_message})
      log_exchange(
        SHEET_URL,
        st.session_state["session_id"],
        user_message = task,
        bot_message= first_message,
        condition=condition
      )
      st.session_state.init_task = True


    #display chat history
    for msg in st.session_state.messages:
      if msg["role"] in ["user","bot"]:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])

    #prevent user from typing after session ended
    if st.session_state.ended:
      st.info("The session has ended. Thank you for participating!")
      #st.stop()
    else:
      if prompt := st.chat_input("Type your message here..."):
        st.chat_message ("user").markdown(prompt)

        #detect 'ready to begin' prompt from user and start with 1st scene
        if not st.session_state.started and any (word in prompt.lower() for word in ["start"]):
          st.session_state.round = 1
          st.session_state.started = True
        elif not st.session_state.started:
          st.chat_message("bot").markdown("Please type **'start'** to start the session!")

        if st.session_state.round > 0:
          st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.round == 7:
          #chat round 7: final reflection
          reflection_q = (
          "Our session is comming to an end. Looking back at this experience, what did you learn or realize about your preferences regarding refugees?"
          )
          st.chat_message("bot").markdown(reflection_q)
          st.session_state.messages.append({"role": "bot", "content": reflection_q})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message=reflection_q,
            condition= condition
          )
        elif st.session_state.round == 8:
          #chat round 8: closing message
          closing_msg = (
            "Thank you for participating! This concludes our session."
          )
          st.chat_message("bot").markdown(closing_msg)
          st.session_state.messages.append({"role": "bot", "content": closing_msg})
          st.session_state.ended = True

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message=closing_msg,
            condition= condition
          )

        elif st.session_state.round == 1:
          start_msg = ( "Welcome! Please feel free to share any thoughts or concerns you may have about refugees.")
          st.chat_message ("bot").markdown(start_msg)
          st.session_state.messages.append({"role": "bot", "content" : start_msg})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message= start_msg,
            condition= condition
          )

        elif 1 <= st.session_state.round <= 6:
          scene_hint = (
            "Respond directly to the participant’s statement by acknowledging their feelings in varied, natural ways and inviting deeper reflection." 
            "Maintain a calm, empathetic, and respectful tone." 
            "Ask one open-ended question at a time that encourages perspective-taking (e.g., daily life in camps, emotions after displacement, sources of hope)." 
            "Never repeat the same question twice." 
            "Keep facilitator messages brief (2 to 3 sentences maximum) to allow space for warmth and reflection." 
            "If the participant changes the topic, gently remind them to stay focused on refugees."
          )
          st.session_state.messages.append({"role": "system", "content": scene_hint})
          
          #add system reminders for robustness
          if st.session_state.round in [3, 5]:
            system_reminder=(
              "Reminder: You are a compassionate facilitator guiding a reflective conversation about refugees." 
              "Stay empathetic, warm, and supportive." 
              "Focus on helping the participant connect emotionally with refugee experiences." 
              "Alternate between brief validations, reflective statements, and occasional open-ended questions that invite perspective-taking." 
              "Vary your acknowledgments; avoid repeating the same phrases." 
              "Not every turn needs a question — some can simply reflect or paraphrase the participant’s feelings." 
              "Keep responses concise (2 to 3 sentences maximum, no lists)." 
              "Do not give advice, facts, or solutions." 
              "If the participant changes the topic, gently remind them to stay focused on refugees."
            )
            # add to conversation context but dont display it
            st.session_state.messages.append({"role": "system", "content": system_reminder})

          #build full conversation (so model sees context)
          conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
          ])

          bot_reply = ask_llm(conversation_text)

          st.chat_message("bot").markdown(bot_reply)
          st.session_state.messages.append({"role": "bot", "content": bot_reply})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message= bot_reply,
            condition= condition
          )

        if st.session_state.started:
          show_progress(st.session_state.round - 1, total_rounds)
          st.session_state.round += 1


  ###Control Group1: Neutral Chatbot ###
  elif condition == "neutral":

    #total rounds
    total_rounds = 5

    # mobile friendly
    st.set_page_config(
      page_title ="Neutral Chatbot",
      layout="wide",
      initial_sidebar_state="collapsed"
    )
    #streamlit UI
    st.title("Neutral Chatbot")


    if not st.session_state.init_task:
      # add system role/facilitator introduction
      # do it also only once for this session
      task = ("You are a chatbot facilitator guiding a light reflective discussion with a participant about preferences and experiences related to cats and dogs."
              "Keep the conversation neutral and engaging without introducing strong opinions, emotional topics or factual arguments."
              " Focus in exploring personal perspectives, comparisons, and general reflections."
              "Conversation Structure:"
              "1.Introduction Phase: Begin with a warm, friendly introduction explaining that this is a short, casual discussion about cats and dogs."
              "Set a neutral, conversational tone and ask if the participant is ready to begin."
              "When the participant indicates readiness, begin the first discussion topic."
              "2. Discussion Phase (6 rounds):"
              "Guide the participant through six short, conversational topics about cats, dogs, and people’s relationships with them."
              "In each topic:"
              "- Ask one open, friendly question about the participant’s preferences or experiences."
              "- Keep your tone neutral, warm, and conversational."
              "- Avoid taking sides or offering factual claims (e.g., about breeds, health benefits, etc.)."
              "- Keep each facilitator message short (2 to 3 sentences maximum). "
              "3. Closing Phase: After the sixth topic, invite the participant to reflect on the discussion as a whole."
              "Ask one light, reflective question such as: 'After this chat, do you think you’ve learned anything new about your own preferences?'"
              "End with a short, friendly thank-you message."
              "Style Guidelines:"
              "- Maintain a warm, neutral tone throughout."
              "- Avoid introducing any factual claims or controversial statements."
              "- Keep messages short (2 to 3 sentences)."
              "- Encourage equal attention to both cats and dogs; don’t favor one side."
              "- Stay conversational and friendly, focusing on engagement and reflection."
              "- Please only ask one question at a time."
              "- Dont let the participant change the topic. In that case remind them to stay on the topic of cats and dogs."
      )
      intro_answer = ask_llm(task)
      #st.session_state.messages.append({"role": "bot", "content": intro_answer})

      first_message = ( "Welcome to this brief exercise.\n\n "
                        "In this exercise, you will interact with a chatbot to answer questions about your preferences and opinions " 
                        "regarding cats and dogs. The chatbot will guide the conversation by asking questions and providing prompts for you to reflect on.\n\n "
                        "When you feel ready, just type in **'start'**, and we will begin the first scene."
      )

      st.session_state.messages.append({"role": "bot", "content": first_message})
      log_exchange(
        SHEET_URL,
        st.session_state["session_id"],
        user_message = task,
        bot_message= first_message,
        condition=condition
      )
      st.session_state.init_task = True


    #display chat history
    for msg in st.session_state.messages:
      if msg["role"] in ["user","bot"]:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])

    #prevent user from typing after session ended
    if st.session_state.ended:
      st.info("The session has ended. Thank you for participating!")
      #st.stop()
    else:
      prompt = st.chat_input("Type your message here...")
      if prompt:
        st.chat_message ("user").markdown(prompt)

        #detect 'ready to begin' prompt from user and start with 1st scene
        if not st.session_state.started and any (word in prompt.lower() for word in ["start"]):
          st.session_state.round = 1
          st.session_state.started = True
        elif not st.session_state.started:
          st.chat_message("bot").markdown("Please type 'start' to start the session!")

        if st.session_state.round > 0:
          st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.round == 5:
          #chat round 5: final reflection
          reflection_q = (
        "Our session is comming to an end. Looking back at this experience, what did you learn or realize about your preferences regarding cats and dogs?"
          )
          st.chat_message("bot").markdown(reflection_q)
          st.session_state.messages.append({"role": "bot", "content": reflection_q})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message=reflection_q,
            condition= condition
          )
        elif st.session_state.round == 6:
          #chat round 6: closing message
          closing_msg = (
            "Thank you for participating! This concludes our session."
          )
          st.chat_message("bot").markdown(closing_msg)
          st.session_state.messages.append({"role": "bot", "content": closing_msg})
          st.session_state.ended = True

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message=prompt,
            bot_message=closing_msg,
            condition= condition
          )
        elif 1 <= st.session_state.round <= 4:
          system_hint = (
            "The participant has confirmed they are ready to begin."
            "Now start the discussion."
            "Ask a question on cats and dogs in 2 to 3 short sentences,"
            "so that the particpant feels encouraged o examine their own preferences and reasoning."
            "Please only ask one question at a time."
            "Do not add headings to the topics or factual details. Stay in the facilitator role."
            "Dont let the participant change the topic. In that case remind them to stay on the topic of cats and dogs."
          )
          st.session_state.messages.append({"role": "system", "content": system_hint})
          
          #add system reminders for robustness
          if st.session_state.round in [2, 4]:
            system_reminder=(
              "Reminder: You are a facilitator guiding a light discussion about cats and dogs. "
              "Stay friendly and balanced, encouraging the participant to share their thoughts and experiences."
              "Ask one open, reflective question at a time. "
              "Do not offer advice or solutions. Keep your response brief (2 to 3 sentences, no bullet lists). Do not introduce new factual information."
              "Remember to move naturally through the topics."
              "Dont let the participant change the topic. In that case remind them to stay on the topic of cats and dogs."
            )
            # add to conversation context but dont display it
            st.session_state.messages.append({"role": "system", "content": system_reminder})

          #build full conversation (so model sees context)
          conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
          ])

          bot_reply = ask_llm(conversation_text)

          st.chat_message("bot").markdown(bot_reply)
          st.session_state.messages.append({"role": "bot", "content": bot_reply})

          log_exchange(
            SHEET_URL,
            st.session_state["session_id"],
            user_message= prompt,
            bot_message= bot_reply,
            condition= condition
          )
        
        if st.session_state.started:
          show_progress(st.session_state.round - 1, total_rounds)
          st.session_state.round += 1


  ###Control Group2: Flyer ###
  elif condition == "flyer":
      st.info(f"Please read the following text carefully.")
      st.title("Refugee Fact Sheet")
      st.subheader("Understanding Refugees")

      st.markdown("""
                  This short flyer provides background information on refugee experiences around the world. \n
                  By the end of June 2025 117.3 million people worldwide had been forcibly displaced due to persecution, conflict, violence or human rights violations.
                  Refugees are protected under international law, within the right to seek asylum and not be returned to danger.\n
                  ***These conflicts are responsible for the displacement of millions of people:***
                  The war in Sudan has led to the world's largest displacement crisis, affecting 13.4 million people. 
                  Millions of people are fleeing the democratic Republic of Congo, Myanmar, Ukraine and the Gaza Strip.\n
                  ***No one flees voluntarily:***
                  The reasons for fleeing can vary greatly. In most cases, it is war and violence that force people to leave their homes. 
                  Especially when the fear for one’s own life or for the lives of children, family and friends is always present.\n
                  ***Refugees in host countries:***
                  Refugees are received in host countries through policies that aim to support their integration. 
                  The OECD highlights that early access to language courses, employment programs, and integration services is essential. 
                  The recognition of foreign qualifications and vocational training helps them enter the labor market more quickly.\n
                  Employment outcomes vary. For example, in Germany, seventy percent of immigrants were employed in 2022, which is higher than the EU average. 
                  Refugee women with young children face more challenges as only forty percent are employed.\n
                  Health systems also play a crucial role. The WHO reports that refugees often experience poorer health outcomes than host populations. 
                  Barriers include limited access to healthcare services, language differences, and social exclusion.\n
                  Overall, data shows that refugees face challenges in education, employment, and health, however host countries can improve conditions by adapting their policies.

                  For more details feel free to check out:\n
                  OECD: https://sdg.iisd.org/news/oecd-highlights-integration-policies-for-refugees-and-migrants or https://home-affairs.ec.europa.eu/whats-new/publications/oecd-report-germany-status-immigrant-integration_en  
                  WHO: https://www.who.int/health-topics/refugee-and-migrant-health#tab=tab_1   
                  UNCHR: https://www.unhcr.org/refugee-statistics  
                  UNO-Flüchtlingshilfe: https://www.uno-fluechtlingshilfe.de/informieren/fluechtlingszahlen 

      """)

      #log flyer completion
      if "completed_flyer" not in st.session_state:
        st.session_state.ended = True
        st.session_state.completed_flyer = True
        log_exchange(
          SHEET_URL,
          st.session_state["session_id"],
          user_message= "Flyer completed",
          bot_message= "Flyer content shown",
          condition = "flyer"
        )

  if st.session_state.ended == True:
    base_url = "https://lmubwl.eu.qualtrics.com/jfe/form/SV_dnYJg2pu3kLolfM"
    # Build query string safely
    params = {
      "PROLIFIC_PID": st.session_state.get("prolific_pid", ""),
      "STUDY_ID": st.session_state.get("prolific_study_id", ""),
      "SESSION_ID": st.session_state.get("prolific_session_id", ""),
      "BOT_TYPE": st.session_state.condition
    }

    query_string = urllib.parse.urlencode(params)
    # Final compiled link
    final_url = f"{base_url}?{query_string}"

    st.info(f"[Please click here to continue to Post-Survey]({final_url})")
    