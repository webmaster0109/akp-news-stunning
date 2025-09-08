from django.shortcuts import render, redirect
from akp_accounts.models import CustomUser

# views.py
import shutil
import tempfile
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404, HttpResponseForbidden, HttpResponseServerError

def _is_superuser(user):
    return user.is_active and user.is_superuser

@login_required
@user_passes_test(_is_superuser)
def db_download_page(request):
    """
    Renders a simple page with a download button and a progress slider.
    Only active superusers can access.
    """
    return render(request, template_name="admin_tools/db_download.html")

@login_required
@user_passes_test(_is_superuser)
def download_sqlite_db(request):
    """
    Copies the configured DB file to a temporary file and streams it back as an attachment.
    Using a temp copy reduces the chance of reading a DB mid-write.
    """
    db_settings = settings.DATABASES.get("default", {})
    db_name = db_settings.get("NAME")
    if not db_name:
        return HttpResponseServerError("Database path not configured in settings.DATABASES['default']['NAME'].")

    db_path = Path(db_name)
    if not db_path.is_absolute():
        base = Path(settings.BASE_DIR)
        db_path = (base / db_path).resolve()

    # Accept common sqlite suffixes
    if db_path.suffix not in {".sqlite3", ".sqlite"}:
        return HttpResponseServerError(
            f"Configured database does not look like an SQLite file (suffix={db_path.suffix}): {db_path}"
        )

    if not db_path.exists():
        raise Http404("Database file not found.")

    try:
        # Make a temporary copy to avoid reading while DB may be written to
        tmp = tempfile.NamedTemporaryFile(prefix="db_copy_", suffix=db_path.suffix, delete=False)
        tmp_name = tmp.name
        tmp.close()
        shutil.copy2(str(db_path), tmp_name)

        # Stream the temp file. Caller (developer) is responsible for cleaning temp files occasionally.
        # We set content-length automatically since FileResponse wraps a file object.
        f = open(tmp_name, "rb")
        response = FileResponse(f, as_attachment=True, filename=db_path.name)
        return response
    except Exception as exc:
        return HttpResponseServerError(f"Failed to prepare database file: {exc}")

def admin_dashboard(request):
    return render(request, template_name='admin/index.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(username=username, password=password).first()

        if not user:
            return redirect('admin_login')

        if user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('admin_login')

    return render(request, template_name='admin/login.html')