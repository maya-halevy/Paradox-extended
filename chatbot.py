"""
This file runs the entire program (main), simply run the script and the chat will begin in the console.
"""

import openai
import constants
import sys
import os


def call_router_chatbot(input_message):
    """
    Calls the router model to get a classification if the user is ready to register or not.
    :param: input_message: (str): The message from the user.
    :return: str: True or False
    Exception: If an error occurs during the API call.
    """
    try:
        conversation_history = [{"role": "system", "content": constants.ROUTER_MODEL_PERSONA}]  # set the model persona
        conversation_history.extend(
            constants.ROUTER_TRAINING_SAMPLES + [{"role": "user", "content": input_message}])

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation_history
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e} call_registration_chatbot")
        sys.exit(1)


def call_registration_chatbot(input_message, conversation_history):
    """
    Calls the registration model to get necessary info for registration.
    :param: input_message: (str): The message from the user.
    :return: str: Chatbot response
    Exception: If an error occurs during the API call.
    """
    try:
        conversation_history.extend([{"role": "system", "content": constants.REGISTRATION_MODEL_PERSONA},
                                     {"role": "user", "content": input_message}])

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation_history
        )
        reply = completion.choices[0].message.content
        conversation_history.extend([{"role": "assistant", "content": reply}])
        return reply, conversation_history
    except Exception as e:
        print(f"An error occurred: {e} call_registration_chatbot")
        sys.exit(1)


def call_parsing_chatbot(input_message):
    """
    Calls the parsing model to gather the necessary registration info from the conversation.
    :param: input_message: (str): The message from the user.
    :return: str: dictionary format {variable : value}
    Exception: If an error occurs during the API call.
    """
    try:
        conversation_history = [{"role": "system", "content": constants.PARSER_MODEL_PERSONA}]  # set the model persona
        conversation_history.extend(
            constants.PARSER_TRAINING_SAMPLES + [{"role": "user", "content": input_message}])

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation_history
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e} call_registration_chatbot")
        sys.exit(1)


def call_inquiry_chatbot(input_message):
    """
    Calls the chatbot model to get a response to the user's question.
    :param: input_message: (str): The message from the user to which the chatbot will respond.
    :return: str: chatbot's response to the input message.
    Exception: If an error occurs during the API call.
    """
    try:
        conversation_history = [{"role": "system", "content": constants.INQUIRY_MODEL_PERSONA}]  # set the model persona
        conversation_history.extend(constants.INQUIRY_TRAINING_SAMPLES + [{"role": "user", "content": input_message}])

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation_history
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e} call_inquiry_chatbot")
        sys.exit(1)


def format_dialog(dialog):
    """
    Extracts the content after 'content' and 'role' from each entry in the dialog,
    and formats it as "Question: '...' Answer: '...'".
    :param: str: the raw conversation between user and chatbot
    :returns: str: formatted conversation
    """
    formatted_output = ""
    for i in range(len(dialog) - 1):
        question = dialog[i]['content']
        answer = dialog[i + 1]['content']
        formatted_output += f"Question: '{question}' Answer: '{answer}'"

    return formatted_output


def main():
    """
    Main function to run the chatbot interface. Manages the user interaction with the chatbot, handling registration
    and responding to queries. Continues running until the user decides to exit. :return:
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    openai.api_key = api_key

    print("\n*** Welcome to GenAI Summer Camp! *** \n\nTo leave the conversation, type 'exit' at any time."
          "\n\nHi there! I'm Jennifer, how can I help you today?\n")

    while True:
        user_input = input().strip()

        # ensure there is input
        while not user_input:
            user_input = input('Please enter a question\n').strip()

        # opportunity to exit program
        if user_input in ['exit', 'quit']:
            break

        else:
            # router chatbot to check if user is ready to register
            if call_router_chatbot(user_input).strip() == 'True':  # register camper

                conversation_history = []
                camper_info = []
                camper_registered = False

                while True:

                    question, conversation = call_registration_chatbot(user_input, conversation_history)
                    print('\nJennifer:', question, '\n')
                    if camper_registered:
                        break
                    user_input = input().strip()
                    if user_input in ['exit', 'quit']:
                        break
                    conversation.extend([{'role': 'user', 'content': user_input}])

                    # send Q and A to parsing bot
                    conversation_clean = format_dialog(conversation[-2:])
                    info = call_parsing_chatbot(conversation_clean)
                    print(info)

                    if info != "False":
                        camper_info.append(info)
                    if len(camper_info) == 5:
                        camper_registered = True  # break when all info is received
                break  # exit program after camper is registered
            else:
                # inquiry chatbot
                response = call_inquiry_chatbot(user_input)
                print('\nJennifer:', response, '\n')

    print('Thank you!')
    sys.exit(1)


if __name__ == "__main__":
    main()
