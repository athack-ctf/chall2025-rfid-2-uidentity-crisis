from smartcard.System import readers
from smartcard.util import toHexString
import time

### USE THIS SCRIPT IS CARD IS GEN 1 (backdoor card)

NEW_UID = [0x11, 0x22, 0x33, 0x44]  # Replace with desired UID


def format_print(array):
    return ' '.join('{:02x}'.format(x).upper() for x in array)



def connect_reader():
    """Finds and connects to the first available NFC reader."""
    r = readers()
    if not r:
        print("No smartcard readers found.")
        return None
    reader = r[0]
    print(f"Using reader: {reader}")
    conn = reader.createConnection()
    conn.connect()
    return conn

def read_current_uid(conn):
    """Reads the current UID from the card."""
    # Get UID: Cla (FF) Ins (CA) P1 (00) P2 (00) Len (00)
    apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    response, sw1, sw2 = conn.transmit(apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        uid = response  # Truncate to 4 bytes if longer
        print(f"Current UID: {toHexString(uid)}")
        return uid
    else:
        print(f"Failed to read UID (SW1={sw1:02X}, SW2={sw2:02X})")
        return None


def authenticate_magic_card(conn):
    """Authenticate block 0 on a Magic Card (Required before writing UID)."""
    # FF 86 P1=0 (memory key) P2=0 (slot) Length=0x05 (5 bytes) 01 address=00 00 auth=60 (key A) 00
    auth_apdu = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x00, 0x60, 0x00]
    response, sw1, sw2 = conn.transmit(auth_apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        print("Authentication successful.")
        return True
    else:
        print(f"Authentication failed (SW1={sw1:02X}, SW2={sw2:02X})")
        return False    

def read_block_0(conn):
    """Reads the current block 0 from the card."""
    # Get UID: Cla (FF) Ins (B0) P1 (address MSB 00) P2 (address LSB 00) Len (XX = 0x10)
    apdu = [0xFF, 0xB0, 0x00, 0x00, 0x10]
    response, sw1, sw2 = conn.transmit(apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        block_0 = response  # Truncate to 4 bytes if longer
        print(f"Current block 0: {toHexString(block_0)}")
        return block_0
    else:
        print(f"Failed to read block 0 (SW1={sw1:02X}, SW2={sw2:02X})")
        return None


def send_magic_backdoor(conn):
    """Sends Magic Backdoor Commands (40 and 43)."""


    response, sw1, sw2 = conn.transmit(build_direct_command([0x40]))
    if response and response[0] == 0x0A:
        print("Magic command 40 accepted (Response: A)")
    else:
        print("Magic command 40 failed!")
        return False

    response, sw1, sw2 = conn.transmit(build_direct_command([0x43]))
    if response and response[0] == 0x0A:
        print("Magic command 43 accepted (Response: A)")
        return True
    else:
        print("Magic command 43 failed!")
        return False



def build_direct_command(command):
    direct_command_prefix = [0xFF, 0x00, 0x00, 0x00]
    command = [0xD4, 0x42] + command

    result = direct_command_prefix + [len(command)] + command

    print(f"Direct command: {format_print(result)}")
    return result




def send_halt(conn):
    # FF 00 00 00 + len(data) + data
    
    """Sends HLTA (Halt) command to the card."""
    hlta_apdu = [0x50, 0x00, 0x57, 0xCD]  # HLTA + CRC

    response, sw1, sw2 = conn.transmit(build_direct_command(hlta_apdu))
    print(f"HLTA Sent: SW1={sw1:02X}, SW2={sw2:02X}, response={format_print(response)}")

    
def send_prewrite(conn):
    """Sends HLTA (Halt) command to the card."""
    prewrite_apdu = [0xA0, 0x00, 0x5f, 0xb1]

    response, sw1, sw2 = conn.transmit(build_direct_command(prewrite_apdu))
    print(f"Prewrite Sent: SW1={sw1:02X}, SW2={sw2:02X}")


def calculate_parity_bits(uid):
    """MIFARE uses even parity; calculate parity bits for UID."""
    parity = uid[0] ^ uid[1] ^ uid[2] ^ uid[3]
    print(f"Parity bits {hex(parity)}")
    return [parity]


def write_new_uid(conn, new_uid, block_0):
    """Writes a new UID to a Magic Card."""
    if len(new_uid) != 4:
        print("UID must be exactly 4 bytes for MIFARE Classic 1K.")
        return

    # Construct the full block 0 data
    bcc = calculate_parity_bits(new_uid)
    block_0_data = new_uid + bcc + block_0[5:]  # Manufacturing bytes

    print(f"Block 0 data: {[hex(b) for b in block_0_data]}")

    send_halt(conn)

    # Ensure authentication before writing
    send_magic_backdoor(conn)

    send_prewrite(conn)


    if not len(block_0_data) == 16:
        print("Block 0 MUST be 16 bytes")
        return
    
    print("WRITING")


    # Write UID to block 0
    # FF D6 address (00 00) 10 (length block = 16) + data (len 16)
    write_apdu = [0xFF, 0xD6, 0x00, 0x00, 0x10] + block_0_data
    response, sw1, sw2 = conn.transmit(write_apdu)

    if sw1 == 0x90 and sw2 == 0x00:
        print(f"Successfully changed UID to: {toHexString(new_uid)}")
    else:
        print(f"Failed to write new UID (SW1={sw1:02X}, SW2={sw2:02X})")

    write_apdu = [0x11, 0x22, 0x33, 0x44, 0x44, 0x08, 0x04, 0x00, 0x46, 0x59, 0x25, 0x58, 0x49, 0x10, 0x23, 0x02, 0xAA, 0xD5]
    response, sw1, sw2 = conn.transmit(write_apdu)

    if sw1 == 0x90 and sw2 == 0x00:
        print(f"Successfully changed UID to: {toHexString(new_uid)}")
    else:
        print(f"Failed to write new UID (SW1={sw1:02X}, SW2={sw2:02X})")


if __name__ == "__main__":
    conn = connect_reader()
    if conn:
        current_uid = read_current_uid(conn)
        if current_uid:
            if authenticate_magic_card(conn):
                block_0 = read_block_0(conn)
                print("Attempting to rewrite UID...")
                time.sleep(0.2)  # Wait before writing
                write_new_uid(conn, NEW_UID, block_0)

                
