# Targets
- ByteWeight
  - Linux
    - [coreutils-8.31](https://ftp.gnu.org/gnu/coreutils/coreutils-8.31.tar.xz)
    - [binutils-2.32](https://ftp.gnu.org/gnu/binutils/binutils-2.32.tar.xz)
    - [findutils-4.7.0](https://ftp.gnu.org/pub/gnu/findutils/findutils-4.7.0.tar.xz)
  - Windows?
    - putty
    - 7zip
    - vim
    - libsodium
    - libetpan
    - HID API 
    - pbc
- Trending From Github (2019.10.13) w/ release version
  - [nettdata/netdata](https://github.com/netdata/netdata/archive/v1.18.0.zip)
  - [commanderx16/x16-emulator](https://github.com/commanderx16/x16-emulator/archive/r33.zip)
  - [alibaba/AliOS-Things](https://github.com/alibaba/AliOS-Things/archive/v3.0.0.zip)
  - [mit-pdos/xv6-public](https://github.com/mit-pdos/xv6-public/archive/xv6-rev11.zip)
  - [espressif/esp-idf](https://github.com/espressif/esp-idf/archive/v3.1.6.zip)
  - [openssl/openssl](https://github.com/openssl/openssl/archive/OpenSSL_1_1_1d.zip)
  - [esp8266/Arduino](https://github.com/esp8266/Arduino/archive/2.5.2.zip)
  - [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT/archive/2019.07.zip)
  - [ShadowsocksR-Live/shadowsocksr-native](https://github.com/ShadowsocksR-Live/shadowsocksr-native/archive/0.6.zip)
  - [mpv-player/mpv](https://github.com/mpv-player/mpv/archive/v0.29.1.zip)

# Model
## Beginning
```
/* overall description, copyright, etc
 * or NULL
 */
// Or look like this

# include or define or if (anything starts with #)
# define xxx \
  xxxx
```

## Function
```
/* Function description
 * .....
 */
static int func(.., .., ..) {
}
```
## Skip elements
- #.....
- enum
- struct

# Assumptions
- Collect comments before function declarations
- The collecting process starts after last `#include` (in c-like languages)
- Skip #* 

# Patches
## oleo
configure
```
delete 6299a6300,6472
```
