# How to Solve the Challenge?

- Install the whole nfc/acr122u_pcsc/pcscd stack
```
sudo pcscd -f --disable-polkit

libnfc --with-drivers=acr122_pcsc
make clean in between
./utils/nfc-scan-device works
```


- Take a fresh UID writable card

`nfc-mfsetuid deadbeef`

Need to disconnect the reader after, and restart the pcscd