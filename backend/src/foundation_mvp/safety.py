import re,stat,zipfile
from pathlib import PurePosixPath
ALLOWED={'.dxf','.dwg','.xlsx','.pdf','.zip','.json'}
MAX_FILE=600*1024*1024
MAX_ARCHIVE=1024*1024*1024
class InputError(ValueError): pass
def filename(name):
 if not name or len(name)>220 or name in ('.','..') or any(c in name for c in '/\\\x00') or any(ord(c)<32 for c in name): raise InputError('Invalid file name')
 suffix=PurePosixPath(name).suffix.lower()
 if suffix not in ALLOWED: raise InputError('Supported files: DXF, DWG, PDF, XLSX, ZIP and reviewed-input JSON')
 return suffix
def archive_members(path):
 try:
  with zipfile.ZipFile(path) as z:
   infos=z.infolist()
   if len(infos)>2000 or sum(i.file_size for i in infos)>MAX_ARCHIVE: raise InputError('Archive exceeds expanded size or member limit')
   names=set()
   for i in infos:
    p=PurePosixPath(i.filename)
    if p.is_absolute() or '..' in p.parts or '\\' in i.filename or ':' in i.filename or '\x00' in i.filename or stat.S_ISLNK(i.external_attr>>16) or i.flag_bits&1: raise InputError('Archive contains unsafe, linked or encrypted entries')
    if i.filename.casefold() in names: raise InputError('Archive contains duplicate member names')
    names.add(i.filename.casefold())
   return infos
 except zipfile.BadZipFile: raise InputError('Unreadable ZIP archive') from None
