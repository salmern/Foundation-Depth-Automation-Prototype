"""No-network runtime prerequisite diagnostic; prints no secrets."""
import importlib.util,json,shutil,sys
modules=['fastapi','pydantic','uvicorn','multipart','ezdxf','shapely','openpyxl','pytest','httpx']
report={'python':sys.version.split()[0],'python_modules':{m:importlib.util.find_spec(m) is not None for m in modules},'commands':{c:shutil.which(c) is not None for c in ['node','npm','pdftotext']}}
report['backend_dependencies_available']=all(report['python_modules'].values())
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['backend_dependencies_available'] else 1)
