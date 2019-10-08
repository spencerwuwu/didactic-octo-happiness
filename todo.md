# Targets
- ByteWeight
  - Linux
    - coreutils
    - binutils
    - findutils
  - Windows?
    - putty
    - 7zip
    - vim
    - libsodium
    - libetpan
    - HID API 
    - pbc

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

