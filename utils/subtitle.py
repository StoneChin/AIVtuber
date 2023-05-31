def generate_subtitle(chat):
    # chat.txt will be used to display the chat/question on OBS
    with open("chat.txt", "w", encoding="utf-8") as outfile:
        try:
            lines = [chat[i:i+50] for i in range(0, len(chat), 50)]
            for line in lines:
                outfile.write("".join(line) + "\n")
        except:
            print("Error writing to chat.txt")
