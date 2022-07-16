def split_info(msg_decodeds):
    msg_decoded_clear = []
    msg_decodeds = msg_decodeds.split("}{")
    for msg_decoded in msg_decodeds:
        if msg_decoded[0] == "{" and msg_decoded[-1] != "}":
            msg_decoded_clear.append(msg_decoded + "}")
            continue

        if msg_decoded[0] != "{" and msg_decoded[-1] != "}":
            msg_decoded_clear.append("{" + msg_decoded + "}")
            continue

        if msg_decoded[-1] == "}" and msg_decoded[0] != "{":
            msg_decoded_clear.append("{" + msg_decoded)
            continue
        msg_decoded_clear.append(msg_decoded)
    return msg_decoded_clear
