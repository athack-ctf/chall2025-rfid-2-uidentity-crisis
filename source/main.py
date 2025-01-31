import curses
import time
from pyfiglet import Figlet
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardConnection import CardConnection
import time


DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
# TARGET_UID = "04 D3 7A 1F 88 68 80"  # Replace with the UID to check against
TARGET_UID = "6C DC 2E 03 07 4F 0C"


def draw_ascii_text(stdscr, ascii_art, y):
    max_width = curses.COLS - 2
    max_height = curses.LINES - 2
    
    if y + len(ascii_art) > max_height:
        return  # Avoid drawing outside screen
    
    x_offset = max(1, (max_width - max(map(len, ascii_art))) // 2)
    for i, line in enumerate(ascii_art):
        if len(line) > max_width:
            line = line[:max_width]  # Truncate long lines
        try:
            stdscr.addstr(y + i, x_offset, line)
        except curses.error:
            pass  # Ignore out-of-bounds errors

def draw_border(stdscr):
    height, width = stdscr.getmaxyx()
    for x in range(1, width-1):
        stdscr.addch(1, x, '=')  # Top border
        stdscr.addch(height - 2, x, '=')  # Bottom border
    for y in range(1, height-1):
        stdscr.addch(y, 1, '|')  # Left border
        stdscr.addch(y, width - 2, '|')  # Right border

    stdscr.addch(1, 1, '+')  # Top-left corner
    stdscr.addch(1, width - 2, '+')  # Top-right corner
    stdscr.addch(height - 2, 1, '+')  # Bottom-left corner
    stdscr.addch(height - 2, width - 2, '+')  # Bottom-right corner

def scroll_message(stdscr, scroll, speed=30):

    big = Figlet(font='big')  # Choose a large ASCII font
    mailbox = big.renderText("Mailbox").split('\n')

    message_len = max([len(row) for row in scroll])

    scroll_height = curses.LINES // 2
    scroll_pos = 10

    while True:
        stdscr.erase()

        draw_border(stdscr)

        draw_ascii_text(stdscr, mailbox, 3)
    
        # Draw scrolling message safely
        for index, line in enumerate(scroll):
            overflow = message_len + scroll_pos - (curses.COLS - 1)
            if (overflow > 0):
                displayed_line = line[:-overflow]
                overflowed_line = line[-overflow:]

                stdscr.addstr(index + scroll_height, 1, overflowed_line)
                stdscr.addstr(index + scroll_height, scroll_pos, displayed_line)
            else:
                displayed_line = line
                stdscr.addstr(index + scroll_height, scroll_pos, displayed_line)
        
        
        # Footer
        stdscr.addstr(curses.LINES - 3, (curses.COLS - len("University Inbox Access System")) // 2, "University Inbox Access System", curses.A_BOLD)
        stdscr.addstr(curses.LINES - 2, (curses.COLS - len(" ~ Software v7.0 ~ ")) // 2, " ~ Software v7.0 ~ ", curses.A_BOLD)
        
        stdscr.refresh()
        
        scroll_pos = ((scroll_pos) % (curses.COLS - 1)) + 1 

        time.sleep(1/speed)



# Helper function to load a key into the ACR122U's key storage
def load_key(card_connection, key_number):
    load_key_apdu = [0xFF, 0x82, 0x00, key_number, 0x06] + DEFAULT_KEY
    response, sw1, sw2 = card_connection.transmit(load_key_apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        print(f"Key loaded successfully into slot {key_number}.")
    else:
        raise Exception(f"Failed to load key (SW1={sw1:02X}, SW2={sw2:02X}).")
    


def main(stdscr):

    with open('flag.txt', 'r') as f:
        flag = f.read().strip()

    available_readers = readers()
    if not available_readers:
        print("No smartcard readers found.")
        return

    reader = available_readers[0]
    print(f"Using reader: {reader}")
    connection = reader.createConnection()


    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(0)  # Block input
    stdscr.clear()
    

    draw_border(stdscr)

    f = Figlet(font='big')  # Choose a large ASCII font
    ascii_art = Figlet(font='big').renderText("Log in with access card").split('\n')
    draw_ascii_text(stdscr, ascii_art, curses.LINES // 4)

    stdscr.refresh()

    while True:
        try:
            connection.connect(CardConnection.T0_protocol | CardConnection.T1_protocol)
            
            # Read UID (Block 0)
            read_uid_apdu = [0xFF, 0xCA, 0x00, 0x00, 0x07]
            response, sw1, sw2 = connection.transmit(read_uid_apdu)
            
            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(response)
                # print(f"Card UID: {uid}")

                # stdscr.clear()

                if uid == TARGET_UID:
                    ntgreek = Figlet(font='doom', width = 400)  # Choose a large ASCII font
                    scroll = ntgreek.renderText(flag).split('\n')

                    scroll_message(stdscr, scroll)

                else:
                    scroll = [f"Wrong UID: {uid}"]
                    scroll_message(stdscr, scroll, speed=10)
            
            time.sleep(5)  # Wait 5 seconds before continuing
        except Exception as e:
            # print(f"Error: {e}")
            time.sleep(1)  # Short delay before retrying


    stdscr.clear()
    scroll_message(stdscr)
    
    
   

if __name__ == "__main__":
    curses.wrapper(main)
