class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def logg(type: str = None, text=""):
    """Color print and logg"""
    if type == "header":
        print(bcolors.HEADER + str(text) + bcolors.ENDC)
        return

    if type == "okblue":
        print(bcolors.OKBLUE + str(text) + bcolors.ENDC)
        return

    if type == "okcyan":
        print(bcolors.OKCYAN + str(text) + bcolors.ENDC)
        return

    if type == "okgreen":
        print(bcolors.OKGREEN + str(text) + bcolors.ENDC)
        return

    if type == "warning":
        print(bcolors.WARNING + str(text) + bcolors.ENDC)
        return

    if type == "fail":
        print(bcolors.FAIL + str(text) + bcolors.ENDC)
        return

    if type == "bold":
        print(bcolors.BOLD + str(text) + bcolors.ENDC)
        return

    if type == "underline":
        print(bcolors.UNDERLINE + str(text) + bcolors.ENDC)
        return

    print(str(text))
