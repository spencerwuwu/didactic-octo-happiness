/* Define at-style functions like fstatat, unlinkat, fchownat, etc.
   Copyright (C) 2006, 2009-2019 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* written by Jim Meyering */

#include "dosname.h" /* solely for definition of IS_ABSOLUTE_FILE_NAME */

#ifdef GNULIB_SUPPORT_ONLY_AT_FDCWD
# include <errno.h>
# ifndef ENOTSUP
#  define ENOTSUP EINVAL
# endif
#else
# include "openat.h"
# include "openat-priv.h"
# include "save-cwd.h"
#endif

#ifdef AT_FUNC_USE_F1_COND
# define CALL_FUNC(F)                           \
  (flag == AT_FUNC_USE_F1_COND                  \
    ? AT_FUNC_F1 (F AT_FUNC_POST_FILE_ARGS)     \
    : AT_FUNC_F2 (F AT_FUNC_POST_FILE_ARGS))
# define VALIDATE_FLAG(F)                       \
  if (flag & ~AT_FUNC_USE_F1_COND)              \
    {                                           \
      errno = EINVAL;                           \
      return FUNC_FAIL;                         \
    }
#else
# define CALL_FUNC(F) (AT_FUNC_F1 (F AT_FUNC_POST_FILE_ARGS))
# define VALIDATE_FLAG(F) /* empty */
#endif

/* Call AT_FUNC_F1 to operate on FILE, which is in the directory
   open on descriptor FD.  If AT_FUNC_USE_F1_COND is defined to a value,
   AT_FUNC_POST_FILE_PARAM_DECLS must include a parameter named flag;
   call AT_FUNC_F2 if FLAG is 0 or fail if FLAG contains more bits than
   AT_FUNC_USE_F1_COND.  Return int and fail with -1 unless AT_FUNC_RESULT
   or AT_FUNC_FAIL are defined.  If possible, do it without changing the
   working directory.  Otherwise, resort to using save_cwd/fchdir,
   then AT_FUNC_F?/restore_cwd.  If either the save_cwd or the restore_cwd
   fails, then give a diagnostic and exit nonzero.  */
int 
main
(void) { 
    /* inline comment */
    return 0;
}

static
void func1
(int arg1, int arg2) { return;}
